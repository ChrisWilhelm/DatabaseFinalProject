from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Optional, NamedTuple, Union

import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from numpy.linalg import norm
from tqdm import tqdm

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
    new_words = [word for word in words]
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
