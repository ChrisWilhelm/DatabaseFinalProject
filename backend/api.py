from fastapi import FastAPI
import uvicorn
import pickle
from sqlitedict import SqliteDict
import os
from utils import *
from typing import Optional, Iterable
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pytz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

db_path = os.path.join(app.root_path, "db")
if not os.path.exists(db_path):
    os.makedirs(db_path)

# query db stores the results of queries for later use
query_db_path = os.path.join(db_path, "queries.db")
# query map is a map of queries to vectors
query_map_path = os.path.join(db_path, "query_map.db")
doc_vecs_db_path = os.path.join(db_path, "doc_vecs.db")


def setup_db():
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    doc_vecs_db = SqliteDict(doc_vecs_db_path)
    article_weights = ArticleWeights(5, 1, 5)
    for i, article in enumerate(articles):
        key = i
        vec = article2vec(article, article_weights)
        news_article = Document(
            doc_id=key,
            title=article.title,
            summary=article.summary,
            link=article.url,
            vector=vec,
            date=article.publish_date,
            publisher=article.news_source.name,
            rating=article.news_source.rating.name,
            site_link=article.news_source.url
        )
        doc_vecs_db[key] = news_article
    doc_vecs_db.commit()
    doc_vecs_db.close()


def clear_db(db_path):
    doc_vecs_db = SqliteDict(db_path)
    for key in doc_vecs_db.keys():
        del doc_vecs_db[key]
    doc_vecs_db.commit()
    doc_vecs_db.close()


@app.get("/query")
async def get_articles(q: str,
                       n_results: Optional[int] = 20,
                       result_range: Optional[tuple] = None):
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
        sim_score = sim(q1, vector)
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
    results_with_score = [(doc_id, sim(query_vec, doc_vec))
                          for doc_id, doc_vec in doc_pairs]
    results_with_score = sorted(results_with_score, key=lambda x: -x[1])
    results = [x[0] for x in results_with_score]
    return results


# returns true if doc sim is greater than threshold
def threshold_filter(doc_vector, query_vector, thresh, sim):
    return sim(doc_vector, query_vector) > thresh


# Returns all documents within a specific threshold level
def search_by_threshold(query_vec: BagOfWordsVector, doc_pairs: list, thresh: float, sim=cosine_sim) -> list:
    results = filter(lambda doc_id, doc_vec:
                     threshold_filter(doc_vec, query_vec, thresh, sim), doc_pairs)
    return [pair[0] for pair in results]


# returns k nearest neighbor documents
def search_by_knn(query_vec: BagOfWordsVector, doc_pairs: list, k: int, sim=cosine_sim) -> list:
    results = sort_by_sim(query_vec, doc_pairs, sim=sim)
    return results[:k]


def get_nearest(query_vec: BagOfWordsVector,
                k=20,
                thresh=0,
                sim=cosine_sim) -> list:
    # Generate tuple list with entries in the form of (<doc_id>, <doc_vector>)
    db = SqliteDict(doc_vecs_db_path)
    doc_pairs = [(key, value.vector) for key, value in db.items()]
    db.close()
    if thresh != 0:
        results = search_by_threshold(query_vec, doc_pairs, thresh, sim=sim)
    else:
        results = search_by_knn(query_vec, doc_pairs, k, sim=sim)
    return results


@app.post("/query/update")
def relevance_feedback():
    return


if __name__ == "__main__":
    #clear_db(doc_vecs_db_path)
    clear_db(query_map_path)
    clear_db(query_db_path)
    #setup_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
