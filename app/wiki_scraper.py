import requests

WIKI_API_URL = "https://pt.wikipedia.org/w/api.php"

def get_wikipedia_article(term):
    """
    Recebe um termo e devolve o conteúdo bruto (resumo) da Wikipédia em português.
    """
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

# Teste rápido
if __name__ == "__main__":
    artigo = get_wikipedia_article("Inteligência artificial")
    print(f"🔹 Artigo: {artigo['title']}\n")
    print(f"{artigo['content'][:1000]}...")
