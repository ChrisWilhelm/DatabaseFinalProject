import pickle
from api import remove_repeat_articles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_types import *
from random import random

percent_articles_to_keep : float = 0.1

engine = create_engine("mysql+pymysql://21fa_cwilhel8:Lg9CYYSiMP@dbase.cs.jhu.edu/21fa_cwilhel8_db")
Session = sessionmaker(bind = engine)
session = Session()


def news_source_exists(article):
    return session \
     .query(NewsSource.NewsSourceID) \
     .filter_by(NewsSourceName=article.news_source.name) \
     .first() is not None


def add_news_source(article):
    if not news_source_exists(article):
        news_source = NewsSource(
            NewsSourceName=article.news_source.name,
            Homepage=article.news_source.url,
            BiasID=article.news_source.rating
        )
        session.add(news_source)
        session.commit()

if __name__ == "__main__":
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    articles = remove_repeat_articles(articles)
    for article in articles:
        add_news_source(article)

        news_source_id = session.query(NewsSource.NewsSourceID)\
            .filter(name=article.news_source.name)\
            .first()

        new_article = Article(
            Aname=article.title,
            URL=article.url,
            PublishDate=article.publish_date,
            NewsSourceID=news_source_id,
            ArticleText=article.text,
            ArticleSummary=article.summary
        )
        session.add(new_article)
        session.commit()
        break

    result = session.query(Article).all()
    for row in result:
        print("Title: ", row.Aname)