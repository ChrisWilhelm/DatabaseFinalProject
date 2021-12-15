from sqlalchemy import create_engine, MetaData, desc
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
    word_string = str(word)
    data = (session.query(Article.ArticleID).filter(HasKeyWord.ArticleID == Article.ArticleID)
                 .filter(HasKeyWord.KeyWordID == KeyWord.KeyWordID).filter(KeyWord.KeyWord == word_string)
                 .order_by(desc(Article.PublishDate)).all())
    result = []
    for d in data:  # had to get rest of the data separately because of memory sort issue
        result.append(session.query(Article).filter(Article.ArticleID == d[0]).all())
    return result




def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
