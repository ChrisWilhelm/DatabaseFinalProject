from typing import NamedTuple, Union
from numpy.linalg import norm
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from newspaper import Article
from collections import defaultdict

stop_words = set(stopwords.words('english'))
# typedefs
BagOfWordsVector = dict[str, float]


class Document(NamedTuple):
    doc_id: int
    link: str
    title: str
    summary: str
    vector: dict

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


def article2vec(article: Article, weights: ArticleWeights) -> BagOfWordsVector:
    '''
    Transforms instance of class Article into sparse vector representation
    '''
    vec = defaultdict(float)
    for word in article.keywords:
        vec[word] += weights.keywords
    for word in article.authors:
        vec[word] += weights.authors
    vec[article.news_source.name] += weights.news_source
    return vec


def string2vec(sentence: str) -> BagOfWordsVector:
    '''
    converts a query string into a sparse word vector
    '''
    words = word_tokenize(sentence)
    new_words = [word for word in words if word.isalnum()]
    vec = {}
    for word in new_words:
        vec[word] = 1
    return vec


# run all query preprocessing from this function
def process_query(sentence: str):
    #TODO: nlp preprocessing steps, spellcheck
    return string2vec(sentence)






