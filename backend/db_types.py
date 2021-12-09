from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Article(Base):
    __tablename__ = "Articles"
    ArticleID = Column(Integer, primary_key=True, nullable=False)
    Aname = Column(Text, nullable=False)
    URL = Column(Text, nullable=False)
    PublishDate = Column(DateTime)
    NewsSourceID = Column(Integer)
    ArticleText = Column(Text)
    ArticleSummary = Column(Text)


class WroteBy(Base):
    __tablename__ = "WroteBy"
    ArticleID = Column(Integer, ForeignKey("Article.ArticleID"),
        primary_key=True)
    AuthorID = Column(Integer, ForeignKey("Author.AuthorID"),
        primary_key=True)


class Author(Base):
    __tablename__ = "Author"
    AuthorID = Column(Integer, primary_key=True)
    FName = Column(Text)
    LName = Column(Text, nullable=False)


class BiasType(Base):
    __tablename__ = "BiasType"
    BiasID = Column(Integer, primary_key=True, nullable=False)
    BiasName = Column(String(10), nullable=False)


class NewsSource(Base):
    __tablename__ = "NewsSource"
    NewsSourceID = Column(Integer, primary_key=True, nullable=False)
    NewsSourceName = Column(Text, nullable=False)
    Homepage = Column(Text, nullable=False)
    BiasID = Column(Integer, ForeignKey("BiasType.BiasID"))

