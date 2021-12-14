from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.serializer import loads, dumps
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


@app.get("/keyword/{word}")
async def root(word):
    wordString = str(word)
    data = dumps(session.query(Article).filter(HasKeyWord.ArticleID == Article.ArticleID).filter(HasKeyWord.KeyWordID == KeyWord.KeyWordID).filter(KeyWord.KeyWord == wordString).all())
    query2 = loads(data, metadata, Session)
    return query2


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()