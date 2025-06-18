import requests
import re

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

def get_wikipedia_article(term):
    """
    Retrieves the content of a Wikipedia article by its title.
    Returns a dictionary with 'title' and 'content'.
    """
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": term,
        "redirects": 1
    }

    try:
        response = requests.get(WIKI_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            print(f"--- No pages found for '{term}'")
            return {"title": term, "content": ""}

        page = next(iter(pages.values()))
        title = page.get("title", term)
        content = page.get("extract", "")

        return {
            "title": title,
            "content": content
        }
    except requests.exceptions.RequestException as e:
        print(f"--- Network error fetching Wikipedia article '{term}': {e}")
        return {"title": term, "content": ""}
    except Exception as e:
        print(f"--- Error processing Wikipedia article '{term}': {e}")
        return {"title": term, "content": ""}


def search_wikipedia(query, max_results=5):
    """
    Performs a search on Wikipedia and returns a list of article titles.
    """
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": max_results
    }

    try:
        response = requests.get(WIKI_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        if "query" in data and "search" in data["query"]:
            for item in data["query"]["search"]:
                results.append(item["title"])
        return results
    except requests.exceptions.RequestException as e:
        print(f"--- Network error searching Wikipedia for '{query}': {e}")
        return []
    except Exception as e:
        print(f"--- Error processing Wikipedia search for '{query}': {e}")
        return []

def extract_keywords(text, min_length=3):
    """
    Extracts keywords from a given text, filtering out common stop words.
    """
    stopwords = {"a", "an", "the", "and", "or", "in", "on", "is", "of", "to", "for", "with", "by", "about", "like", "from", "but", "not", "what", "which", "who", "whom", "whose", "where", "when", "why", "how"}

    words = re.findall(r'\w+', text.lower())

    keywords = [word for word in words if len(word) >= min_length and word not in stopwords]

    return keywords

def get_relevant_articles(question, max_articles=3):
    """
    Based on the user's question, identifies and returns relevant articles.
    """
    keywords = extract_keywords(question)

    search_query = " ".join(keywords) if len(keywords) >= 2 else question
    if not search_query.strip():
        search_query = question

    print(f"--- Searching Wikipedia for titles based on query: '{search_query}'")
    article_titles = search_wikipedia(search_query, max_results=max_articles)
    
    if not article_titles:
        print("--- No article titles found from Wikipedia search.")
        if search_query != question:
            print(f"--- Retrying Wikipedia search with original question: '{question}'")
            article_titles = search_wikipedia(question, max_articles=max_articles)
            if not article_titles:
                return []

    articles = []
    for title in article_titles:
        try:
            article = get_wikipedia_article(title)
            if article["content"].strip() and article["title"].strip():
                articles.append(article)
        except Exception as e:
            print(f"--- Error retrieving {title}: {e}")

    return articles

if __name__ == "__main__":
    question = "How do artificial neural networks work?"
    print(f"--- Searching articles for: '{question}'")

    retrieved_articles = get_relevant_articles(question, max_articles=3)

    if retrieved_articles:
        print(f"\n--- Retrieved {len(retrieved_articles)} articles: ---")
        for article in retrieved_articles:
            print(f"--- Title: {article['title']}")
            print(f"--- Content snippet: {article['content'][:200]}...")
            print("-" * 20)
    else:
        print("--- No articles were retrieved for the question.")
