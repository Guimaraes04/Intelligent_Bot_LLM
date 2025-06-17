import requests
import re

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"  # Changed to English Wikipedia

def get_wikipedia_article(term):

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": term,
        "redirects": 1
    }

    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    title = page.get("title", "")
    content = page.get("extract", "")

    return {
        "title": title,
        "content": content
    }

def search_wikipedia(query, max_results=5):

    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": max_results
    }

    response = requests.get(WIKI_API_URL, params=params)
    data = response.json()

    results = []
    if "query" in data and "search" in data["query"]:
        for item in data["query"]["search"]:
            results.append(item["title"])

    return results

def extract_keywords(text, min_length=4):
    """
    Extracts keywords from a question to improve search
    """
    stopwords = {"the", "a", "an", "and", "is", "are", "was", "were", "in", "on", "at",
               "to", "for", "with", "by", "about", "like", "from", "but", "not", "or",
               "what", "which", "who", "whom", "whose", "where", "when", "why", "how"}

    words = re.findall(r'\w+', text.lower())

    keywords = [word for word in words if len(word) >= min_length and word not in stopwords]

    return keywords

def get_relevant_articles(question, max_articles=3):
    """
    Based on the user's question, identifies and returns relevant articles
    """
    keywords = extract_keywords(question)

    search_query = " ".join(keywords) if len(keywords) >= 2 else question

    article_titles = search_wikipedia(search_query, max_results=max_articles)

    articles = []
    for title in article_titles:
        try:
            article = get_wikipedia_article(title)
            if article["content"].strip():
                articles.append(article)
                print(f"✅ Retrieved: {article['title']} - {len(article['content'])} characters")
        except Exception as e:
            print(f"❌ Error retrieving {title}: {e}")

    return articles

if __name__ == "__main__":
    question = "How do artificial neural networks work?"
    print(f"🔍 Searching articles for: '{question}'")

    articles = get_relevant_articles(question)
    print(f"\n📚 Found {len(articles)} relevant articles")

    for article in articles:
        print(f"\n🔹 Article: {article['title']}")
        print(f"{article['content'][:300]}...")