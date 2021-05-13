import os
import pickle
from argparse import ArgumentParser

import pytz
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlitedict import SqliteDict

from custom_types import Story
from utils import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

db_path = os.path.join(app.root_path, "db")
if not os.path.exists(db_path):
    os.makedirs(db_path)

# query db stores the results of queries for later use
query_db_path = os.path.join(db_path, "queries.db")
# query map is a map of queries to vectors
query_map_path = os.path.join(db_path, "query_map.db")
doc_vecs_db_path = os.path.join(db_path, "doc_vecs.db")


def remove_repeat_articles(articles: list[Story]) -> list[Story]:
    new_article_info = set()
    new_articles = []
    for article in articles:
        if (article.news_source.name, article.title) not in new_article_info:
            new_articles.append(article)
            new_article_info.add((article.news_source.name, article.title))
    return new_articles


def setup_db() -> None:
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    articles = remove_repeat_articles(articles)
    doc_vecs_db = SqliteDict(doc_vecs_db_path)
    article_weights = ArticleDataWeights(author=5, keywords=3, summary=1, title=4, publisher=5)
    article_data = [ArticleData(
        title=tokenize_string(article.title),
        summary=tokenize_string(article.summary),
        keywords=article.keywords,
        author=article.authors,
        publisher=[article.news_source.name]) for article in tqdm(articles,
                                                                  total=len(articles),
                                                                  desc="Pre-processing: Tokenizing data")]
    vectors = generate_doc_tfidfs(article_data, article_weights)
    for i, article in enumerate(tqdm(articles,
                                     total=len(articles),
                                     desc="Pre-processing: Adding vectors to database")):
        key = i
        news_article = Document(
            doc_id=key,
            title=article.title,
            summary=article.summary,
            link=article.url,
            vector=vectors[i],
            date=article.publish_date,
            publisher=article.news_source.name,
            rating=article.news_source.rating.name,
            site_link=article.news_source.url
        )
        doc_vecs_db[key] = news_article
    doc_vecs_db.commit()
    doc_vecs_db.close()


def clear_db(db_path_shadow: str) -> None:
    doc_vecs_db = SqliteDict(db_path_shadow)
    print("Clearing db {}".format(db_path_shadow))
    for key in tqdm(doc_vecs_db.keys()):
        del doc_vecs_db[key]
    doc_vecs_db.commit()
    doc_vecs_db.close()


@app.get("/query")
async def get_articles(q: str, n_results: Optional[int] = 20) -> dict:
    # first see if we have a cached result
    results, processed_query = check_for_cached_result(q)
    if len(results) > 0:
        return {"results": results}
    else:
        search_results = get_new_search_results(q, processed_query, n_results)
        return {"results": sort_search_by_date(search_results)}


# Isolate function to generate new search results in case queries need to be updated
def get_new_search_results(q: str, processed_query: BagOfWordsVector, k: int) -> list:
    search_results = []
    doc_ids = get_nearest(processed_query, k=k)
    doc_db = SqliteDict(doc_vecs_db_path)
    # Extract document information based on ids
    for doc_id in doc_ids:
        document = doc_db[doc_id]
        doc_dict = {
            "doc_id": document.doc_id,
            "title": document.title,
            "summary": document.summary,
            "link": document.link,
            "date": document.date if hasattr(document, "date") else datetime.min.replace(tzinfo=pytz.UTC),
            "rating": document.rating,
            "publisher": document.publisher,
            "site": document.site_link
        }
        search_results.append(doc_dict)

    doc_db.close()
    # Add query we haven't seen to db
    query_map_db = SqliteDict(query_map_path)
    query_map_db[q] = processed_query
    query_map_db.commit()
    query_map_db.close()

    query_db = SqliteDict(query_db_path)
    query_db[q] = search_results
    query_db.commit()
    query_db.close()
    return search_results


def get_key_from_document(document) -> datetime:
    if document["date"] is not None:
        return document["date"].replace(tzinfo=pytz.UTC)
    else:
        return datetime.min.replace(tzinfo=pytz.UTC)


def sort_search_by_date(search_results: list) -> list:
    return sorted(search_results, key=get_key_from_document, reverse=True)


# Check db to see if we've precomputed a similar query already
def check_for_cached_result(query: str, thresh: float = 0.8, sim=cosine_sim) -> tuple:
    query_map = SqliteDict(query_map_path)
    query_results = SqliteDict(query_db_path)
    # see if we have computed this exact query before
    try:
        result = query_results[query]
        query_vec = query_map[query]
        query_map.close()
        query_results.close()
        return result, query_vec
    except KeyError:
        pass
    # If not, see if any query is close enough
    processed_query = process_query(query)
    max_sim_query, score = get_max_sim(processed_query, query_map.items(), sim=sim)
    if score > thresh:
        result = query_results[max_sim_query]
        query_map.close()
        query_results.close()
        return result
    query_map.close()
    query_results.close()
    return [], processed_query


def get_max_sim(q1: BagOfWordsVector,
                queries: Iterable[tuple[str, BagOfWordsVector]],
                sim=cosine_sim) -> tuple[str, float]:
    max_sim_query = ""
    max_sim_score = -1
    for query, vector in queries:
        sim_score = sim(q1, string2vec(query))
        if sim_score > max_sim_score:
            max_sim_score = sim_score
            max_sim_query = query
    return max_sim_query, max_sim_score


# Returns sorted list of document ids according to some similarity metric
def sort_by_sim(query_vec: BagOfWordsVector, doc_pairs: list, sim=cosine_sim) -> list:
    """
        Linear search through documents. doc_pairs must be a tuple list of
        (<doc_id>, <sparse_doc_vector>) tuples
        """
    results_with_score = sorted(((doc_id, sim(query_vec, doc_vec))
                                 for doc_id, doc_vec in doc_pairs),
                                key=lambda item: item[1],
                                reverse=True)
    return [item[0] for item in results_with_score]


# returns true if doc sim is greater than threshold
def threshold_filter(doc_vector, query_vector, thresh, sim):
    return sim(doc_vector, query_vector) > thresh


# Returns all documents within a specific threshold level
def search_by_threshold(query_vec: BagOfWordsVector, doc_pairs: list, thresh: float, sim=cosine_sim) -> list:
    results = filter(lambda doc_id, doc_vec:
                     threshold_filter(doc_vec, query_vec, thresh, sim), doc_pairs)
    return [pair[0] for pair in results]


# returns k nearest neighbor documents
def search_by_knn(query_vec: BagOfWordsVector, doc_pairs: list, k: int, sim=cosine_sim,
                  return_all: bool = False) -> list:
    results = sort_by_sim(query_vec, doc_pairs, sim=sim)
    return results if return_all else results[:k]


def get_nearest(query_vec: BagOfWordsVector,
                k: int = 20,
                thresh: int = 0,
                sim=cosine_sim,
                return_all: bool = False) -> list:
    # Generate tuple list with entries in the form of (<doc_id>, <doc_vector>)
    db = SqliteDict(doc_vecs_db_path)
    doc_pairs = [(key, value.vector) for key, value in db.items()]
    db.close()
    if thresh != 0:
        results = search_by_threshold(query_vec, doc_pairs, thresh, sim=sim)
    else:
        results = search_by_knn(query_vec, doc_pairs, k, sim=sim, return_all=return_all)
    return results


class QueryUpdate(BaseModel):
    q: str
    undo: bool
    relevant: Optional[list[int]] = None
    irrelevant: Optional[list[int]] = None


@app.post("/query/update")
async def relevance_feedback(body: QueryUpdate) -> None:
    if not body.undo:
        update_query(body.q, body.relevant, body.irrelevant)
    else:
        undo_update_query(body.q, body.relevant, body.irrelevant)


def update_query(q: str,
                 relevant: list[int] = None,
                 irrelevant: list[int] = None,
                 alpha=0.9,
                 beta=0.1) -> None:
    query_vector = try_to_get_query_from_db(q)
    query_vector = add_docs_to_query_vector(query_vector, relevant, alpha)
    query_vector = subtract_docs_from_query_vector(query_vector, irrelevant, beta)
    put_query_in_map_db(q, query_vector)
    get_new_search_results(q, query_vector, k=20)


def undo_update_query(q: str,
                      relevant: list[int] = None,
                      irrelevant: list[int] = None,
                      alpha: float = 0.9,
                      beta: float = 0.1) -> None:
    query_vector = try_to_get_query_from_db(q)
    query_vector = add_docs_to_query_vector(query_vector, irrelevant, alpha)
    query_vector = subtract_docs_from_query_vector(query_vector, relevant, beta)
    put_query_in_map_db(q, query_vector)
    get_new_search_results(q, query_vector, k=20)


def try_to_get_query_from_db(q: str) -> BagOfWordsVector:
    query_map = SqliteDict(query_map_path)
    try:
        query_vector = query_map[q]
        query_map.close()
        return query_vector
    except KeyError:
        query_map.close()
        raise HTTPException


def add_docs_to_query_vector(query_vector: BagOfWordsVector,
                             docs: list[int],
                             alpha: float) -> BagOfWordsVector:
    doc_db = SqliteDict(doc_vecs_db_path)
    for doc_id in docs:
        doc_vector = try_to_get_doc_vector_from_db(doc_id, doc_db)
        query_vector = add_vectors(query_vector, scalar_multiply(doc_vector, alpha))
    doc_db.close()
    return query_vector


def try_to_get_doc_vector_from_db(doc_id: int, doc_db: SqliteDict) -> BagOfWordsVector:
    vector = {}
    try:
        vector = doc_db[doc_id].vector
    except KeyError:
        pass
    return vector


def subtract_docs_from_query_vector(query_vector: BagOfWordsVector,
                                    docs: list[int],
                                    beta: float) -> BagOfWordsVector:
    doc_db = SqliteDict(doc_vecs_db_path)
    for doc_id in docs:
        doc_vector = try_to_get_doc_vector_from_db(doc_id, doc_db)
        query_vector = subtract_vectors(query_vector, scalar_multiply(doc_vector, beta))
    doc_db.close()
    return query_vector


def put_query_in_map_db(q: str, query_vector: BagOfWordsVector) -> None:
    query_map = SqliteDict(query_map_path)
    query_map[q] = query_vector
    query_map.commit()
    query_map.close()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--reset_db", dest="reset_db", action="store_true")
    parser.set_defaults(reset_db=False)
    parser.add_argument("--reset_cache", dest="reset_cache", action="store_true")
    parser.set_defaults(reset_cache=False)
    args = parser.parse_args()
    if args.reset_db:
        clear_db(doc_vecs_db_path)
        setup_db()
    if args.reset_cache:
        clear_db(query_map_path)
        clear_db(query_db_path)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
