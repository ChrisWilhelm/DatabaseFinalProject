from concurrent.futures import as_completed, ThreadPoolExecutor
from bs4 import BeautifulSoup, SoupStrainer
from custom_types import NewsSource, Rating
from pickle import dump, HIGHEST_PROTOCOL
from requests import get
from tqdm import tqdm
from typing import Optional
from urllib.parse import urljoin

ALL_SIDES_BASE_URL = 'https://www.allsides.com'


def get_rating_helper(rating: str) -> Rating:
    if rating == 'Left':
        return Rating.LEFT
    elif rating == 'Lean Left':
        return Rating.LEAN_LEFT
    elif rating == 'Center':
        return Rating.CENTER
    elif rating == 'Lean Right':
        return Rating.LEAN_RIGHT
    elif rating == 'Right':
        return Rating.RIGHT
    elif rating == 'Mixed':
        return Rating.MIXED
    else:
        raise ValueError(f'An unknown rating "{rating}" was encountered')


def process_news_source(news_source) -> Optional[NewsSource]:
    # News source's name is found in the first "td" tag
    name = news_source.find('td').a.text
    # Each rating begins with the following prefix string: "AllSides Media Bias Rating: "
    rating = get_rating_helper(news_source.find('img')['alt'][28:])
    # Find URL for this news source by using a proxy (inner) page
    proxy_link = news_source.find('a')['href']
    proxy_html = get(urljoin(ALL_SIDES_BASE_URL, proxy_link)).text
    proxy_bs = BeautifulSoup(proxy_html, 'html.parser', parse_only=SoupStrainer(class_='dynamic-grid'))
    link = proxy_bs.find('a')
    if link is not None:
        url = link['href']
        if url:
            return NewsSource(name, rating, url)
        else:
            return None
    else:
        return None


def main() -> None:
    # Load cached copy of HTML table from AllSides Media Bias Ratings
    with open('media_bias_table.html') as html:
        bs = BeautifulSoup(html, 'html.parser')
    # Split table by rows without first result (table header)
    news_sources = bs('tr')[1:]
    print(f'Found {len(news_sources)} news source candidates')
    # Process each news source in parallel: use thread-based parallelism because IO-bound
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_news_source, news_source) for news_source in news_sources]
        for future in tqdm(as_completed(futures), total=len(futures), desc='Processing Step'):
            result = future.result()
            if result is not None:
                results.append(result)
    print(f'Only {len(results)} news sources were actually valid')
    # Save results using pickle
    with open('news_sources.pickle', 'wb') as outfile:
        dump(results, outfile, protocol=HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
