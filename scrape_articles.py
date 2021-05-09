from concurrent.futures import as_completed, ThreadPoolExecutor

from typing import List

from custom_types import NewsSource, Story
from newspaper import Article, build, Source
from pickle import dump, HIGHEST_PROTOCOL, load
from tqdm import tqdm

CHUNKSIZE = 10


def build_paper_helper(url: str) -> Source:
    paper = build(url,
                  # Assuming 5 characters per English word, each article must be at least 160 characters
                  MIN_WORD_COUNT=100,
                  MAX_TITLE=280,
                  MAX_KEYWORDS=100,
                  request_timeout=10,
                  fetch_images=False,
                  follow_meta_refresh=True,
                  memoize_articles=False)
    paper.download_articles(threads=2)
    return paper


def process_articles_helper(articles: List[Article], news_source: NewsSource) -> List[Story]:
    stories = []
    for article in articles:
        article.nlp()
        stories.append(Story(news_source,
                             article.title,
                             frozenset(article.authors),
                             article.text,
                             article.summary,
                             frozenset(article.keywords)))
    return stories


def main() -> None:
    # Load in parsed news sources
    with open('news_sources.pickle', 'rb') as infile:
        news_sources: List[NewsSource] = load(infile)
    # Build each paper object in parallel: use thread-based parallelism because IO-bound
    papers = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(build_paper_helper, news_source.url) for news_source in news_sources]
        for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc='Building Step')):
            paper: Source = future.result()
            if paper is not None:
                papers.append((i, paper))
    # Parse papers next: cannot use parallelism because `Source` type is not pickle-able
    for _, paper in tqdm(papers, total=len(papers), desc='Parsing Step'):
        paper.parse_articles()
    # Finally, perform NLP step for each article in every paper
    stories = []
    for i, paper in papers:
        stories.extend(process_articles_helper(paper.articles, news_sources[i]))
    print(f'Extracted {len(stories):,} stories total')
    # Save results using pickle
    with open('stories.pickle', 'wb') as outfile:
        dump(stories, outfile, protocol=HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
