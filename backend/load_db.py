import pickle
from api import remove_repeat_articles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.custom_types import Rating
from db_types import *
from random import random

percent_articles_to_keep : float = 0.1
aws_ip = "54.211.230.209"

engine = create_engine("mysql+pymysql://db_final:password@" + aws_ip + "/db_final_db")
# engine = create_engine("mysql+pymysql://21fa_cwilhel8:Lg9CYYSiMP@dbase.cs.jhu.edu/21fa_cwilhel8_db")
Session = sessionmaker(bind = engine)
session = Session()

def determine_bias_id(article):
    if article.news_source.rating == Rating.CENTER:
        return 3
    elif article.news_source.rating == Rating.LEFT:
        return 1
    elif article.news_source.rating == Rating.LEAN_LEFT:
        return 2
    elif article.news_source.rating == Rating.LEAN_RIGHT:
        return 4
    elif article.news_source.rating == Rating.RIGHT:
        return 5
    else:
        return 6


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
            BiasID=determine_bias_id(article)
        )
        session.add(news_source)
        session.commit()


if __name__ == "__main__":
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    articles = remove_repeat_articles(articles)
    # session.query(Article).delete()
    # session.query(NewsSource).delete()
    for article in articles:
        add_news_source(article)

        news_source_id = session.query(NewsSource.NewsSourceID)\
            .filter(NewsSource.NewsSourceName == article.news_source.name)\
            .first()

        new_article = Article(
            Aname=article.title,
            URL=article.url,
            PublishDate=article.publish_date,
            NewsSourceID=news_source_id[0],
            ArticleText=article.text,
            ArticleSummary=article.summary
        )

        # for author in article.authors:
        #     add_author()
        session.add(new_article)
        session.commit()
        break

    result = session.query(Article).all()
    for row in result:
        print("Title: ", row.Aname)