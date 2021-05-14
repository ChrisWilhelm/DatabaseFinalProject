import pickle
import time
from collections import defaultdict
from math import inf
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from GoogleNews import GoogleNews
from sqlitedict import SqliteDict
from tqdm import tqdm

from api import get_nearest, doc_vecs_db_path
from utils import string2vec

NUM_QUERIES = 100
NUM_PAGES = 10


def interpolate(x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float],
                x: Union[int, float]) -> float:
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    return m * x + b


def precision_at(recall: float, results: list[str], relevant: list[str]) -> float:
    rank = {}
    for url in relevant:
        try:
            url_rank = results.index(url) + 1
        except ValueError:
            url_rank = inf
        rank[url] = url_rank
    table = []
    REL = len(relevant)
    for i, doc in enumerate(sorted(relevant, key=lambda link: rank[link])):
        curr_recall = (i + 1) / REL
        curr_precision = (i + 1) / rank[doc]
        if curr_recall == recall:
            return curr_precision
        else:
            table.append((curr_recall, curr_precision))
    if len(table) == 1:
        # Only one entry so interpolate with implicit point
        entry = table[0]
        return interpolate(0, 1, entry[0], entry[1], recall)
    else:
        # We have more than one entry in our table
        table_sorted = sorted(table, key=lambda item: item[0])
        first_entry = table_sorted[0]
        last_entry = table_sorted[-1]
        if recall < first_entry[0]:  # Cannot be equal if here
            return interpolate(0, 1, first_entry[0], first_entry[1], recall)
        elif recall > last_entry[0]:  # Cannot be equal if here
            return interpolate(last_entry[0], last_entry[1], 1, REL / len(results), recall)
        else:
            for i in range(len(table_sorted) - 1):
                prev_entry = table_sorted[i]
                next_entry = table_sorted[i + 1]
                if prev_entry[0] < recall < next_entry[0]:
                    return interpolate(prev_entry[0], prev_entry[1], next_entry[0], next_entry[1], recall)


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
        time.sleep(1)  # Avoid HTTP Error 429: Too Many Requests
        urls = []
        for i in range(1, NUM_PAGES + 1):  # Make sue NUM_PAGES is included
            articles = gn.page_at(i)  # GoogleNews is one-based
            urls.extend([article['link'] for article in articles])
            time.sleep(1)  # Avoid HTTP Error 429: Too Many Requests
        query2urls_relevant[query] = urls
    # Save relevant queries as Pickle file just in case
    with open('relevant_queries.pickle', 'wb') as outfile:
        pickle.dump(query2urls_relevant, outfile, protocol=pickle.HIGHEST_PROTOCOL)
    # Obtain ordering of documents from our system for the same evaluation queries
    query2urls_results = {}
    doc_vecs_db = SqliteDict(doc_vecs_db_path)
    for query, _ in tqdm(queries2count, total=NUM_QUERIES, desc='Our System Step'):
        doc_ids: list[str] = get_nearest(string2vec(query), return_all=True)
        query2urls_results[query] = [doc_vecs_db[doc_id].link for doc_id in doc_ids]
    # Compute precision at
    median_ranks = []
    intersection_sizes = []
    for query, _ in queries2count:
        intersection = set(query2urls_results[query]) & set(query2urls_relevant[query])
        ranks = [query2urls_results[query].index(url) + 1 for url in intersection]
        median_ranks.append(np.median(ranks))
        intersection_sizes.append(len(intersection))
        # recalls = np.linspace(0.0, 1.0)
        # precisions = []
        # for recall in recalls:
        #     precisions.append(precision_at(recall, query2urls_results[query], query2urls_relevant[query]))
        # plt.plot(recalls, precisions)
        # plt.show()
    queries = list(range(1, NUM_QUERIES + 1))  # Make x-axis 1-based
    plt.plot(queries, median_ranks)
    plt.title("Median Rank over Our Ordering w.r.t. Google News")
    plt.xlabel('Query Index')
    plt.ylabel('Median Rank')
    plt.plot(queries, intersection_sizes)
    plt.title("Number of Common Articles between All Relevant and Returned Articles")
    plt.xlabel('Query Index')
    plt.ylabel('Size of Overlap')


if __name__ == '__main__':
    main()
