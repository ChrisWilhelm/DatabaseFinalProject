import pickle

if __name__ == "__main__":
    with open("../stories.pickle", "rb") as fp:
        articles = pickle.load(fp)
    new_article_info = set()
    new_articles = []
    for article in articles:
        if (article.news_source.name, article.title) not in new_article_info:
            new_articles.append(article)
            new_article_info.add((article.news_source.name, article.title))
    print("done")
    print("done")

