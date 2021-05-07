import logging
import sys
import re
from bs4 import BeautifulSoup
from queue import Queue, PriorityQueue
from urllib import parse, request, robotparser
from newspaper import Article

logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')


def parse_links(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)


# Accepts (link, description) pairs
# Could use whatever comparison metric would be useful
# Because we haven't learned any yet, I'm just doing alphabetical order for now
def compare_links(link1, link2):
    return link1[0] < link2[0]


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K



def link_key_fnc():
    return cmp_to_key(compare_links)


# Sort list of links according to compare_links function defined above
def parse_links_sorted(root, html):
    links = parse_links(root, html)
    key_fnc = link_key_fnc()
    return sorted(links, key=key_fnc)


def get_links(url):
    res = request.urlopen(url)
    return list(parse_links(url, res.read()))


# Normalize hosts and check if they are same
def is_nonlocal_link(parsed_original, url: str):
    parsed = parse.urlparse(url)
    if parsed.hostname is None:
        return True
    normalized_host1 = re.sub("www\.", "", parsed_original.netloc)
    normalized_host2 = re.sub("www\.", "", parsed.netloc)
    if normalized_host1 == normalized_host2:
        return False
    return True


# url must be an expanded link
# Normalize host and path, and check if both are the same
def is_self_referencing(parsed_original, url: str):
    parsed_url = parse.urlparse(url)
    normalized_host1 = re.sub("www\.", "", parsed_original.hostname) \
        if parsed_original.hostname is not None else None
    normalized_host2 = re.sub("www\.", "", parsed_url.hostname) \
        if parsed_url.hostname is not None else None
    normalized_path1 = "/" if parsed_original.path == "" else parsed_original.path \
        if parsed_original.path is not None else None
    normalized_path2 = "/" if parsed_url.path == "" else parsed_url.path \
        if parsed_url.path is not None else None
    return normalized_host1 == normalized_host2 \
           and normalized_path1 == normalized_path2


def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    parsed_original = parse.urlparse(url)
    links = get_links(url)
    filtered = filter(lambda x: is_nonlocal_link(parsed_original, x[0]), links)
    return list(filtered)


def convert_absolute(base_url, rel_url):
    rel_url_tokens = rel_url.split("/")
    base_url_tokens = base_url.split("/")
    for tok in rel_url_tokens:
        if tok == "..":
            base_url_tokens.pop()
        elif tok == ".":
            pass
        else:
            base_url_tokens.append(tok)
    return "/".join(base_url_tokens)


def get_content_type(req):
    headers = req.headers._headers
    types = []
    for header in headers:
        if header[0] == "Content-Type":
            types = re.split("[;,]\s+", header[1])
    return types


def relevant_type(types, desired):
    for type in types:
        if type in desired:
            return True
    return False


# Don't get links that aren't web pages
def filter_link(link):
    if link.startswith('mailto'):
        return False
    elif link.endswith('.pdf'):
        return False
    elif link.endswith('.jpg'):
        return False
    elif link.endswith('.png'):
        return False
    elif link.endswith('.pptx'):
        return False
    elif link.endswith('.ppt'):
        return False
    elif link.endswith('.xlsx'):
        return False
    elif link.endswith('.csv'):
        return False
    elif link.endswith('.tsv'):
        return False
    elif link.endswith('.tar'):
        return False
    elif link.endswith('.zip'):
        return False
    elif link.endswith('.h5'):
        return False
    elif link.endswith('.mov'):
        return False
    elif link.endswith('.mp3'):
        return False
    elif link.endswith('.mp4'):
        return False
    elif link.endswith('.wav'):
        return False
    else:
        return True


def is_article(soup):
    return len(soup.find_all('body', {"class": "article-single"})) > 0


def crawl(root, wanted_content=None, within_domain=True):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''

    queue = Queue()
    queue.put(root)

    # Include support for robots.txt files
    robot_parser = robotparser.RobotFileParser()
    visited = set()
    extracted = []
    printed = []
    current_host = ''

    while not queue.empty():
        url = queue.get()
        if url in visited:
            continue
        parsed_url = parse.urlparse(url)
        prev_host = current_host
        current_host = parsed_url.hostname
        print(url)
        printed.append(url)
        try:
            if prev_host != current_host:
                robot_parser.set_url(parse.urljoin('http://' + current_host, 'robots.txt'))
                robot_parser.read()
            req = request.urlopen(url)
            html = req.read()
            soup = BeautifulSoup(html, 'html.parser')

            visited.add(url)
            visitlog.debug(url)

            if wanted_content is not None:
                types = get_content_type(req)
                relevant = relevant_type(types, wanted_content) and is_article(soup)
            else:
                relevant = True

            if relevant:
                extract_information(soup)

            for link, title in parse_links(url, html):
                expanded_url = parse.urljoin(url, link)
                # Check if it's legal to fetch
                if not robot_parser.can_fetch('*', expanded_url):
                    continue
                # Check if file is obviously not a web page
                elif not filter_link(expanded_url):
                    continue
                # Check if link is different and unvisited
                if not is_self_referencing(parsed_url, expanded_url) \
                        and (expanded_url not in visited):
                    # If we only want local links, make sure link is local
                    if within_domain:
                        if not is_nonlocal_link(parsed_url, expanded_url):
                            queue.put(expanded_url)
                    else:
                        queue.put(expanded_url)

        except Exception as e:
            print(e, url)

    return visited, extracted


def extract_information(soup):
    '''Extract contact information from html, returning a list of (url, category, content) pairs,
    where category is one of PHONE, ADDRESS, EMAIL'''

    dates = soup.find_all("div", {"class": "article-date"})
    if len(dates) > 0:
        date = dates[0].text
    else:
        date = "none"
    print(date)


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)


def main():
    # site = sys.argv[1]
    site = 'https://www.foxnews.com/politics/biden-amtrak-story-fact-check-conductor-million-miles'
    links = get_links(site)
    writelines('links.txt', links)

    nonlocal_links = get_nonlocal_links(site)
    writelines('nonlocal.txt', nonlocal_links)

    visited, extracted = crawl(site, wanted_content=["text/html"])
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)


if __name__ == '__main__':
    main()
