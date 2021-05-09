from fastapi import FastAPI
import uvicorn
import pickle
from sqlitedict import SqliteDict
import os
from utils import *
import json

app = FastAPI()

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
            link="https://www.google.com",
            vector=vec
        )
        doc_vecs_db[key] = news_article
    doc_vecs_db.commit()
    doc_vecs_db.close()


@app.get("/query")
async def get_articles(query: str):
    pass


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


def search_by_threshold(query_vec: str, doc_pairs: list, thresh: float, sim=cosine_sim) -> list:
    results = filter(lambda doc_id, doc_vec:
                     threshold_filter(doc_vec, query_vec, thresh, sim), doc_pairs)
    return [pair[0] for pair in results]


def search_by_knn(query_vec: BagOfWordsVector, doc_pairs: list, k: int, sim=cosine_sim) -> list:
    results = sort_by_sim(query_vec, doc_pairs, sim=sim)
    return results[:k]


def get_nearest(query: str, db: SqliteDict, k=20, thresh=0, sim=cosine_sim) -> dict:
    processed_query = string2vec(query)
    # Generate tuple list with entries in the form of (<doc_id>, <doc_vector>)
    doc_pairs = [(key, value.vector) for key, value in db.items()]
    if thresh != 0:
        results = search_by_threshold(processed_query, doc_pairs, thresh)
    else:
        results = search_by_knn(processed_query, doc_pairs, k)
    return {}


if __name__ == "__main__":
    setup_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
