from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Optional, NamedTuple, Union

import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from numpy.linalg import norm
from tqdm import tqdm

from backend.consts import ratings_dict
from db_types  import *
from sqlalchemy import select, create_engine

from condition_parser import *
import re

stop_words = set(stopwords.words('english'))
# typedefs
BagOfWordsVector = dict[str, float]


class Document(NamedTuple):
    doc_id: int
    link: str
    title: str
    summary: str
    vector: dict
    date: Optional[datetime]
    publisher: Optional[str]
    rating: Optional[str]
    site_link: Optional[str]

    def __repr__(self):
        return (f"doc_id: {self.doc_id}\n" +
                f"  link: {self.title}\n")


"""
Define some vector operations so that we can use sparse dictionary representations
"""


def add_vectors(v1: dict, v2: dict) -> dict:
    '''
    add two sparse vector representations
    '''
    keys = set(v1.keys()).union(set(v2.keys()))
    result = {}
    for key in keys:
        result[key] = v1.get(key, 0) + v2.get(key, 0)
    return result


def subtract_vectors(v1: dict, v2: dict) -> dict:
    '''
    subtract two sparse vector representations
    '''
    keys = set(v1.keys()).union(set(v2.keys()))
    result = {}
    for key in keys:
        result[key] = v1.get(key, 0) - v2.get(key, 0)
    return result


def scalar_multiply(vec: dict, alpha: Union[int, float]) -> dict:
    '''
    Scalar multiplication for sparse dict vectors
    '''
    result = {}
    for key, value in vec.items():
        result[key] = alpha * value
    return result


def dictdot(x: dict[str, float], y: dict[str, float]):
    '''
    Computes the dot product of vectors x and y, represented as sparse dictionaries.
    '''
    keys = list(x.keys()) if len(x) < len(y) else list(y.keys())
    return sum(x.get(key, 0) * y.get(key, 0) for key in keys)


def cosine_sim(x, y):
    '''
    Computes the cosine similarity between two sparse term vectors represented as dictionaries.
    '''
    num = dictdot(x, y)
    if num == 0:
        return 0
    return num / (norm(list(x.values())) * norm(list(y.values())))


class ArticleWeights(NamedTuple):
    authors: int
    keywords: int
    news_source: int


def is_useful_word(word):
    if word.isalnum() and word not in stop_words:
        return True
    return False


def tokenize_string(sentence: str) -> Iterable:
    words = word_tokenize(sentence)
    return map(lambda x: x.lower(), filter(is_useful_word, words))


def string2vec(sentence: str) -> BagOfWordsVector:
    '''
    converts a query string into a sparse word vector
    '''
    words = word_tokenize(sentence)
    new_words = [word for word in words if word.isalnum()]
    vec = defaultdict(int)
    for word in new_words:
        vec[word] += 1
    return dict(vec)


# run all query preprocessing from this function
def process_query(sentence: str):
    return string2vec(sentence)


class DocFreqs(Counter):
    def __init__(self):
        super(DocFreqs, self).__init__()
        self.num_docs = 0

    def set_num_docs(self, n):
        self.num_docs = n

    def get_num_docs(self):
        return self.num_docs


class ArticleData(NamedTuple):
    title: Iterable[str]
    summary: Iterable[str]
    author: Iterable[str]
    publisher: Iterable[str]
    keywords: Iterable[str]

    def sections(self):
        return [self.title, self.summary, self.author, self.publisher]


class ArticleDataWeights(NamedTuple):
    title: float
    summary: float
    author: float
    publisher: float
    keywords: float


def compute_doc_freq(documents: Iterable[ArticleData]) -> DocFreqs:
    '''
    Computes document frequency, i.e. how many documents contain a specific word
    '''
    freq = DocFreqs()
    n = 0
    for doc in documents:
        n += 1
        words = set()
        for section in doc.sections():
            for word in section:
                words.add(word)
        for word in words:
            freq[word] += 1
    freq.set_num_docs(n)
    return freq


def compute_tf(doc: ArticleData, weights: ArticleDataWeights):
    vec = defaultdict(float)
    for word in doc.title:
        vec[word] += weights.title
    for word in doc.summary:
        vec[word] += weights.summary
    for word in doc.author:
        vec[word] += weights.author
    for word in doc.publisher:
        vec[word] += weights.publisher
    for word in doc.keywords:
        vec[word] += weights.keywords
    return dict(vec)


def compute_tfidf(doc: ArticleData, doc_freqs: DocFreqs, weights: ArticleDataWeights):
    tf = compute_tf(doc, weights)
    tf_idf = {}
    n = doc_freqs.get_num_docs()
    for word in tf.keys():
        tf_idf[word] = tf[word] * np.log(n / (1 + doc_freqs[word]))
    return tf_idf


def generate_doc_tfidfs(docs: Iterable[ArticleData], weights: ArticleDataWeights,
                        verbose=True) -> list[BagOfWordsVector]:
    doc_freqs = compute_doc_freq(docs)
    vectors = []
    if verbose:
        print("Preprocessing: generating document vectors...")
        for doc in tqdm(docs):
            vectors.append(compute_tfidf(doc, doc_freqs, weights))
    else:
        for doc in docs:
            vectors.append(compute_tfidf(doc, doc_freqs, weights))
    return vectors


class QueryCondition():
    def apply(self, statement):
        return NotImplementedError


class BeforeCondition(QueryCondition):

    def __init__(self, date: datetime):
        self.date = date

    def apply(self, statement):
        return statement.where(Article.PublishDate < self.date)


class AfterCondition(QueryCondition):

    def __init__(self, date: datetime):
        self.date = date

    def apply(self, statement):
        return statement.where(Article.PublishDate > self.date)


class AuthorCondition(QueryCondition):

    def __init__(self, authors_list):
        self.authors = authors_list

    def apply(self, statement):
        for author in self.authors:
            statement = statement.where(
                select(Author)
                    .join(WroteBy)
                    .where(Author.AName == author and Article.ArticleID == WroteBy.ArticleID)
                    .exists()
            )
        return statement


class NewsSourceCondition(QueryCondition):
    def __init__(self, publisher):
        self.publisher = publisher

    def apply(self, statement):
        return statement.where(
            NewsSource.NewsSourceName == self.publisher
        )


class BiasRatingCondition(QueryCondition):
    def __init__(self, bias):
        self.bias_id = ratings_dict[bias]

    def apply(self, statement):
        return statement.where(
            NewsSource.BiasID == self.bias_id
        )


class NullQueryCondition(QueryCondition):
    def apply(self, statement):
        return statement


condition_pattern = re.compile("`.*`")


def create_written_by_condition(raw_author_list: list[str]) -> AuthorCondition:
    authors = []
    for author_name in author_list:
        if author_name != AND_TOKEN:
            authors.append(author_name)
    return AuthorCondition(authors)


def create_written_before_condition(date_string: str) -> BeforeCondition:
    date = datetime.strptime(date_string, "%m-%d-%Y")
    return BeforeCondition(date)


def create_written_after_condition(date_string: str) -> AfterCondition:
    date = datetime.strptime(date_string, "%m-%d-%Y")
    return AfterCondition(date)


def create_published_by_condition(publisher: str) -> NewsSourceCondition:
    return NewsSourceCondition(publisher)


def create_bias_condition(bias: str) -> BiasRatingCondition:
    return BiasRatingCondition(ratings_tok_dict[bias])


def create_condition_object(raw_condition: list) -> QueryCondition:
    if raw_condition[0] == WRITTEN_BY_TOK:
        return create_written_by_condition(raw_condition[1])
    elif raw_condition[0] == WRITTEN_BEFORE_TOK:
        return create_written_before_condition(raw_condition[1])
    elif raw_condition[0] == WRITTEN_AFTER_TOK:
        return create_written_after_condition(raw_condition[1])
    elif raw_condition[0] == PUBLISHED_BY_TOK:
        return create_published_by_condition(raw_condition[1])
    elif raw_condition[0] == BIAS_TOK:
        return create_bias_condition(raw_condition[1])
    else:
        return NullQueryCondition()


def extract_query_conditions(q: str) -> tuple[str, list[QueryCondition]]:
    match = condition_pattern.search(q)
    to_apply = []
    if match is not None:
        conditions = condition_list.parseString(q[match.span()[0]:match.span()[1]])
        for i in range(1, len(conditions) - 1):
            to_apply.append(create_condition_object(conditions[i]))
        q = q[0:match.span()[0]] + q[match.span()[1]:len(q)]
    return q, to_apply


if __name__ == "__main__":
    query = "Biden coronavirus `WRITTEN BEFORE 10-20-2020`"
    extract_query_conditions(query)






