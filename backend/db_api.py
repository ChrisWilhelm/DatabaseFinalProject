from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker, scoped_session
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.serializer import loads, dumps
import datetime
from backend.utils import process_query, BagOfWordsVector, cosine_sim
from db_types import *
from fastapi import FastAPI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
aws_ip = "54.211.230.209"

engine = create_engine("mysql+pymysql://db_final:password@" + aws_ip + "/db_final_db")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
session = Session()
metadata = MetaData(bind=engine)

before = ["before"]
after = ["after"]
on = ["on"]


def remove_repeat_articles(articles: list[Article]) -> list[Article]:
    new_article_info = set()
    new_articles = []
    for article in articles:
        if (article.NewsSourceID, article.Aname) not in new_article_info:
            new_articles.append(article)
            new_article_info.add((article.NewsSourceID, article.Aname))
    return new_articles


@app.get("/query")
async def get_articles(q: str, n_results: int = 20) -> dict:
    processed_query = process_query(q)
    search_results = get_new_search_results(q, processed_query, n_results)
    return {"results": search_results}


def get_new_search_results(q: str, processed_query: BagOfWordsVector, k: int) -> list:
    article_ids = get_nearest(processed_query, k=k)
    return article_ids


def convert_to_datetime(date: str):
    result = date.split("-")
    if len(result) == 1:
        result = result[0].split("/")
    if len(result) != 3:
        return False
    if len(result[2]) != 4:
        return False
    if (len(result[1]) != 1 and len(result[1]) != 2) or (len(result[0]) != 2 and len(result[0]) != 1):
        return False
    formatted_date = datetime.datetime(int(result[2]), int(result[0]), int(result[1]), 0, 0, 0, 0)
    return formatted_date


def get_articles_by_date(date: str, modifier: str):
    article_ids = []
    formatted_date = convert_to_datetime(date)
    if not formatted_date:
        return article_ids
    if modifier in before:
        article_ids += (session.query(Article.ArticleID).filter(Article.PublishDate < formatted_date).all())
    elif modifier in after:
        article_ids += (session.query(Article.ArticleID).filter(Article.PublishDate > formatted_date).all())
    elif modifier in on:
        article_ids += (session.query(Article.ArticleID).filter(Article.PublishDate == formatted_date).all())
    just_articles_ids = []
    for article_id in article_ids:
        just_articles_ids.append(article_id[0])
    return just_articles_ids


def get_nearest(processed_query: BagOfWordsVector,
                k: int = 20,
                thresh: int = 0,
                sim=cosine_sim,
                return_all: bool = False) -> list:
    article_ids = []
    next_date = False
    modifier = ""
    for s in processed_query:
        if next_date:
            next_date = False
            article_ids += get_articles_by_date(s, modifier)
        elif s in before or s in after or s in on:
            next_date = True
            modifier = s
        else:
            article_ids += (get_articles_with_similar(s))
    return article_ids


def get_articles_with_similar(s: str) -> list:
    article_ids = []
    with engine.connect() as conn:
        result = conn.execute("CALL FindSimilarNewssource(%s)", s)
        result2 = conn.execute("CALL FindSimilarKeywords(%s)", s)
        result3 = conn.execute("CALL FindSimilarAuthor(%s)", s)
        for row in result:
            article_ids.append(row["ArticleID"])
        for row in result2:
            article_ids.append(row["ArticleID"])
        for row in result3:
            article_ids.append(row["ArticleID"])
    return article_ids


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
