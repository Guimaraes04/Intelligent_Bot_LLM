import chromadb

client = chromadb.PersistentClient(path="../chroma_db")
collection = client.get_or_create_collection("wiki_articles")


def add_documents(docs: list[dict]):
    """
    Recebe uma lista de artigos (cada um com 'title' e 'content') e adiciona à base de vetores
    """
    for i, doc in enumerate(docs):
        doc_id = f"doc_{i}"
        collection.add(
            documents=[doc["content"]],
            metadatas=[{"title": doc["title"]}],
            ids=[doc_id]
        )
        print(f"✅ Adicionado: {doc['title']}")


def search_similar(query: str, top_k=3):
    """
    Pesquisa os documentos mais semelhantes ao texto da query
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    return results


# Teste de funcionamento
if __name__ == "__main__":
    from wiki_scraper import get_wikipedia_article

    artigo = get_wikipedia_article("Machine Learning")
    add_documents([artigo])

    resultado = search_similar("Como as máquinas aprendem?")
    print("\n🔍 Resultados mais relevantes:")
    for i in range(len(resultado["documents"][0])):
        print(f"\n🔹 {resultado['metadatas'][0][i]['title']}")
        print(resultado['documents'][0][i][:300], "...")
