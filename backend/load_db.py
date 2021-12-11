import pickle
from api import remove_repeat_articles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.custom_types import Rating
from db_types import *
from tqdm import tqdm
from random import random

percent_articles_to_keep : float = 0.3
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


def keyword_exists(word):
    return session.query(KeyWord.KeyWordID).filter(KeyWord.KeyWord == word).first() is not None


def add_keywords(article):
    for keyword in article.keywords:
        if not keyword_exists(keyword):
            key_word = KeyWord(
                KeyWord=keyword
            )
            session.add(key_word)
    session.commit()


def author_exists(AName):
    return session.query(Author.AuthorID).filter(Author.AName == AName).first() is not None


def add_authors(article):
    for author in article.authors:
        if not author_exists(author):
            new_author = Author(
                AName=author
            )
            session.add(new_author)
    session.commit()


def get_news_source(article):
    return session \
     .query(NewsSource) \
     .filter_by(NewsSourceName=article.news_source.name) \
     .first()


def add_news_source(article):
    news_source: NewsSource = get_news_source(article)
    if news_source is None:
        news_source = NewsSource(
            NewsSourceName=article.news_source.name,
            Homepage=article.news_source.url,
<<<<<<< Updated upstream
            BiasID=determine_bias_id(article)
=======
            BiasID=int(article.news_source.rating)
>>>>>>> Stashed changes
        )
        session.add(news_source)
        session.commit()


<<<<<<< Updated upstream
def article_not_included(article):
    news_source_id = session.query(NewsSource.NewsSourceID).filter(NewsSource.NewsSourceName == article.news_source.name).first()
    if news_source_id is None :
        return True
    return session.query(Article).filter(Article.Aname == article.title).filter(Article.NewsSourceID == news_source_id[0]).first() is None
=======
def get_author(author: Author):
    new_author = session.query(Author)\
               .filter_by(FName=author.FName, LName=author.LName)\
               .first()
    return new_author


def generate_author_obj(author : str) -> Author:
    author_name = author.split()
    first_name = author_name[0]
    if len(author_name) > 1:
        last_name = author_name[-1]
    else:
        last_name = ""
    new_author = Author(
        FName=first_name,
        LName=last_name
    )
    return new_author


def add_article(article) -> Article:
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


def add_author(author: str) -> Author:
    new_author: Author = generate_author_obj(author)
    existing_author: Author = get_author(new_author)

    if existing_author is None:
        session.add(new_author)
        session.commit()
        existing_author = new_author

    return existing_author


def add_wrote_by(article_id: int, author_id: int) -> WroteBy:
    new_wrote_by = WroteBy(
        ArticleID=article_id,
        AuthorID=author_id
    )
    session.add(new_wrote_by)
    session.commit()
    return new_wrote_by
>>>>>>> Stashed changes


if __name__ == "__main__":
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    articles = remove_repeat_articles(articles)
<<<<<<< Updated upstream
    # session.query(Article).delete()
    # session.query(NewsSource).delete()
    for article in articles:
        if article_not_included(article):
            add_news_source(article)
            add_keywords(article)
            add_authors(article)
            news_source_id = session.query(NewsSource.NewsSourceID)\
                .filter(NewsSource.NewsSourceName == article.news_source.name)\
                .first()
=======
    session.query(HasKeyWord).delete()
    session.query(WroteBy).delete()
    session.query(Article).delete()
    session.query(NewsSource).delete()
    session.query(Author).delete()
    for article in tqdm(articles):
        if random() > percent_articles_to_keep:
            continue
        add_news_source(article)

        new_article: Article = add_article(article)

        for author in article.authors:
            new_author: Author = add_author(author)

            add_wrote_by(new_article.ArticleID, new_author.AuthorID)
        break
>>>>>>> Stashed changes

            new_article = Article(
                Aname=article.title,
                URL=article.url,
                PublishDate=article.publish_date,
                NewsSourceID=news_source_id[0],
                ArticleText=article.text,
                ArticleSummary=article.summary
            )
            session.add(new_article)
            session.commit()
            article_id = session.query(Article.ArticleID).filter(Article.Aname == new_article.Aname)\
                .filter(new_article.NewsSourceID == Article.NewsSourceID).first()
            for keyword in article.keywords:
                key_wordid = session.query(KeyWord.KeyWordID).filter(KeyWord.KeyWord == keyword).first()
                has_keyword = HasKeyWord(
                    KeyWordID=key_wordid[0],
                    ArticleID=article_id[0]
                )
                session.add(has_keyword)
            session.commit()
            for author in article.authors:
                author_id = session.query(Author.AuthorID).filter(Author.AName == author).first()
                new_written_by = WroteBy(
                    ArticleID=article_id[0],
                    AuthorID=author_id[0]
                )
                session.add(new_written_by)
            session.commit()
            # for author in article.authors:
            #     add_author()
            break
    result = session.query(Article).all()
    for row in result:
        print("Title: ", row.Aname)
