from sqlalchemy import create_engine, MetaData, desc
from sqlalchemy.orm import sessionmaker, scoped_session
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

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
    # word_string = str(word)
    # data = (session.query(Article.ArticleID).filter(HasKeyWord.ArticleID == Article.ArticleID)
    #              .filter(HasKeyWord.KeyWordID == KeyWord.KeyWordID).filter(KeyWord.KeyWord == word_string)
    #              .order_by(desc(Article.PublishDate)).all())
    # result = []
    # for d in data:  # had to get rest of the data separately because of memory sort issue
    #     result.append(session.query(Article).filter(Article.ArticleID == d[0]).all())
    # return result


def get_new_search_results(q: str, processed_query: BagOfWordsVector, k: int) -> list:
    search_results = []
    article_ids = get_nearest(processed_query, k=k)
    return search_results


def get_nearest(processed_query: BagOfWordsVector,
                k: int = 20,
                thresh: int = 0,
                sim=cosine_sim,
                return_all: bool = False) -> list:
    article_ids = []
    for s in processed_query:
        article_ids += (get_articles_with_similar(s))
    return article_ids


def get_articles_with_similar(s: str) -> set:
    article_ids = []
    article_ids += session.query(Article.ArticleID).filter(HasKeyWord.ArticleID == Article.ArticleID)\
        .filter(HasKeyWord.KeyWordID == KeyWord.KeyWordID).filter(KeyWord.KeyWord == s).all()
    article_ids += session.query(Article.ArticleID).filter(Article.NewsSourceID == NewsSource.NewsSourceID)\
        .filter(NewsSource.NewsSourceName.ilike("%" + s + "%")).all()
    article_ids += session.query(Article.ArticleID).filter(Article.ArticleID == WroteBy.ArticleID)\
        .filter(WroteBy.AuthorID == Author.AuthorID).filter(Author.AName.ilike("%" + s + "%")).all()
    return set(article_ids)


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
