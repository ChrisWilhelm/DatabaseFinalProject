import pickle
import argparse
from typing import List

from api import remove_repeat_articles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from backend.custom_types import Rating
from db_types import *
from random import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from consts import *
parser = argparse.ArgumentParser()

parser.add_argument("--percent_upload", type=float, default=0.1)
parser.add_argument("--n_workers", type=int, default=200)
args = parser.parse_args()

percent_articles_to_keep : float = args.percent_upload

engine = create_engine("mysql+pymysql://db_final:password@" + AWS_IP + "/db_final_db")
session_factory = sessionmaker(bind = engine)
Session = scoped_session(session_factory)


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


def keyword_exists(word, session):
    return session.query(KeyWord.KeyWordID).filter(KeyWord.KeyWord == word).first() is not None


def author_exists(AName, session):
    return session\
               .query(Author.AuthorID)\
               .filter(Author.AName == AName)\
               .first() is not None


def get_news_source(article, session):
    return session \
     .query(NewsSource) \
     .filter_by(NewsSourceName=article.news_source.name) \
     .first()


def add_news_source(article, session):
    news_source: NewsSource = get_news_source(article, session)
    if news_source is None:
        news_source = NewsSource(
            NewsSourceName=article.news_source.name,
            Homepage=article.news_source.url,
            BiasID=determine_bias_id(article)
        )
        session.add(news_source)
        session.commit()


def article_not_included(article, session):
    news_source_id = session.query(NewsSource.NewsSourceID).filter(NewsSource.NewsSourceName == article.news_source.name).first()
    if news_source_id is None :
        return True
    return session.query(Article)\
               .filter(Article.Aname == article.title)\
               .filter(Article.NewsSourceID == news_source_id[0])\
               .first() is None


def get_author(author: Author, session):
    new_author = session.query(Author)\
               .filter_by(AName=author.AName)\
               .first()
    return new_author


def generate_author_obj(author : str, session) -> Author:
    new_author = Author(
        AName = author
    )
    return new_author


def add_article(article, session) -> Article:
    news_source_id = session.query(NewsSource.NewsSourceID) \
        .filter_by(NewsSourceName=article.news_source.name) \
        .first()

    new_article = Article(
        Aname=article.title,
        URL=article.url,
        PublishDate=article.publish_date,
        NewsSourceID=news_source_id.NewsSourceID,
        ArticleText=article.text,
        ArticleSummary=article.summary
    )

    session.add(new_article)
    session.commit()
    return new_article


def add_author(author: str, session) -> Author:
    new_author: Author = generate_author_obj(author, session)
    existing_author: Author = get_author(new_author, session)

    if existing_author is None:
        session.add(new_author)
        session.commit()
        existing_author = new_author

    return existing_author


def add_wrote_by(article_id: int, author_id: int, session) -> WroteBy:
    new_wrote_by = WroteBy(
        ArticleID=article_id,
        AuthorID=author_id
    )
    session.add(new_wrote_by)
    session.commit()
    return new_wrote_by


def add_authors(article_id: int, authors: List[str], session):
    for author in authors:
        new_author: Author = add_author(author, session)

        add_wrote_by(article_id, new_author.AuthorID, session)


def find_keyword(word: str, session) -> KeyWord:
    return session.query(KeyWord).filter_by(KeyWord=word).first()


def add_keyword(word: str, session):
    key_word = KeyWord(
        KeyWord=word
    )
    session.add(key_word)
    session.commit()
    return key_word


def add_has_keyword(article_id: int, keyword_id: int, session):
    has_key_word = HasKeyWord(
        KeyWordID=keyword_id,
        ArticleID=article_id
    )
    session.add(has_key_word)
    session.commit()


def add_keywords(article_id: int, keywords: List[str], session):
    for word in keywords:
        key_word = find_keyword(word, session)
        if key_word is None:
            key_word = add_keyword(word, session)

        add_has_keyword(article_id, key_word.KeyWordID, session)


def process_article(article):
    if random() > percent_articles_to_keep:
        return
    session = Session()
    add_news_source(article, session)
    new_article: Article = add_article(article, session)
    add_authors(new_article.ArticleID, article.authors, session)
    add_keywords(new_article.ArticleID, article.keywords, session)
    Session.remove()


if __name__ == "__main__":
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    articles = remove_repeat_articles(articles)
    session = Session()
    # reset DB
    session.query(HasKeyWord).delete()
    session.query(WroteBy).delete()
    session.query(Article).delete()
    session.query(NewsSource).delete()
    session.query(Author).delete()
    session.commit()
    Session.remove()

    # Process articles in parallel
    print("Processing %d articles" % len(articles))
    articles_processed = 0
    with ThreadPoolExecutor(max_workers=args.n_workers) as executor:
        futures = [executor.submit(process_article, article) for article in articles]
        for i, future in enumerate(as_completed(futures)):
            articles_processed += 1
            if articles_processed % 500 == 0:
                print("{n} articles processed".format(n=articles_processed))

    print("Done!")

