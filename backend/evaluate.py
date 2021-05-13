import pickle
from collections import defaultdict

from GoogleNews import GoogleNews
from sqlitedict import SqliteDict
from tqdm import tqdm

from api import get_nearest, doc_vecs_db_path
from utils import string2vec

NUM_QUERIES = 100
NUM_PAGES = 10


def main() -> None:
    # Load in scraped stories
    with open('../stories.pickle', 'rb') as infile:
        stories = pickle.load(infile)
    # Compute keyword frequency where each story contributes once to count
    keyword_freq = defaultdict(int)
    for story in stories:
        keywords = story.keywords
        for keyword in keywords:
            keyword_freq[keyword] += 1
    # Select top NUM_QUERIES keywords by frequency as queries for evaluation
    queries2count = sorted(keyword_freq.items(), key=lambda item: item[1], reverse=True)[:NUM_QUERIES]
    # Set up Google News fetcher for plausible date range of start of 2020 to date after we scraped
    # (to avoid potential boundary condition)
    gn = GoogleNews(lang='en', start='01/01/2020', end='05/07/2021')
    # Poll Google News for evaluation queries and save results
    query2urls_relevant = {}
    for query, _ in tqdm(queries2count, total=NUM_QUERIES, desc='Polling GoogleNews Step'):
        gn.search(query)
        urls = []
        for i in range(1, NUM_PAGES + 1):  # Make sue NUM_PAGES is included
            articles = gn.page_at(i)  # GoogleNews is one-based
            urls.extend([article['link'] for article in articles])
        query2urls_relevant[query] = urls
    # Obtain ordering of documents from our system for the same evaluation queries
    query2url_results = {}
    doc_vecs_db = SqliteDict(doc_vecs_db_path)
    for query, _ in tqdm(queries2count, total=NUM_QUERIES, desc='Our System Step'):
        doc_ids: list[str] = get_nearest(string2vec(query), return_all=True)
        query2url_results[query] = [doc_vecs_db[doc_id].link for doc_id in doc_ids]


if __name__ == '__main__':
    main()
