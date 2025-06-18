import chromadb
import os

CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'chroma_db')
print(f"ChromaDB persistent client path: {CHROMA_DB_PATH}")

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def get_or_reset_wiki_collection():
    """
    Ensures the 'wiki_articles' collection is fresh for a new query.
    It tries to delete it if it exists, then creates it.
    Returns the collection object.
    """
    try:
        client.delete_collection(name="wiki_articles")
        print("--- Existing 'wiki_articles' collection deleted.")
    except Exception as e:
        if "does not exists" in str(e):
            print("--- 'wiki_articles' collection did not exist, proceeding to create.")
        else:
            print(f"--- Error deleting collection 'wiki_articles': {e}")
    
    collection = client.get_or_create_collection("wiki_articles")
    print("--- 'wiki_articles' collection ensured (created or retrieved).")
    return collection


def add_documents(collection, docs: list[dict]): # <-- ADD 'collection' argument
    """
    Receives a list of articles (each with 'title' and 'content') and adds to the vector base.
    Requires a collection object to be passed.
    """
    documents_to_add = [doc["content"] for doc in docs]
    metadatas_to_add = [{"title": doc["title"]} for doc in docs]
    ids_to_add = [f"doc_{hash(doc['title'] + doc['content'])}" for doc in docs]

    filtered_documents = []
    filtered_metadatas = []
    filtered_ids = []
    for i, doc_content in enumerate(documents_to_add):
        if doc_content.strip():
            filtered_documents.append(doc_content)
            filtered_metadatas.append(metadatas_to_add[i])
            filtered_ids.append(ids_to_add[i])
        else:
            print(f"--- Skipping empty document content for: {metadatas_to_add[i].get('title', 'Untitled')}")

    if filtered_documents:
        try:
            # Check for existing IDs only if the collection is not expected to be fresh for every call
            # Given that get_or_reset_wiki_collection() is called before add_documents
            # this peek/filter might be less critical but remains good practice for robustness
            existing_ids_result = collection.peek(limit=len(filtered_ids))
            existing_ids = set(existing_ids_result['ids'])
            
            unique_documents = []
            unique_metadatas = []
            unique_ids = []

            for i in range(len(filtered_ids)):
                if filtered_ids[i] not in existing_ids:
                    unique_documents.append(filtered_documents[i])
                    unique_metadatas.append(filtered_metadatas[i])
                    unique_ids.append(filtered_ids[i])
                else:
                    print(f"--- Skipping already existing document (ID: {filtered_ids[i]}, Title: {filtered_metadatas[i].get('title', 'Untitled')})")

            if unique_documents:
                collection.add(
                    documents=unique_documents,
                    metadatas=unique_metadatas,
                    ids=unique_ids
                )
                for title_meta in unique_metadatas:
                    print(f"--- Added to vector store: {title_meta['title']}")
            else:
                print("--- No new unique documents to add to the vector store.")

        except Exception as e:
            print(f"--- Error adding documents to ChromaDB: {e}")
    else:
        print("--- No valid documents to add to the vector store.")


def search_similar(collection, query: str, top_k=3):
    """
    Searches for documents most similar to the query text.
    Requires a collection object to be passed.
    Returns the raw results from ChromaDB.
    """
    if collection.count() == 0:
        print("--- Vector store collection is empty. Cannot perform search.")
        return {'ids': [[]], 'distances': [[]], 'metadatas': [[]], 'embeddings': [[]], 'documents': [[]]}

    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        return results
    except Exception as e:
        print(f"--- Error during vector store search: {e}")
        return {'ids': [[]], 'distances': [[]], 'metadatas': [[]], 'embeddings': [[]], 'documents': [[]]}


if __name__ == "__main__":
    from wiki_scraper import get_wikipedia_article

    print("\n--- Running standalone vector_store.py test ---")
    
    test_collection = get_or_reset_wiki_collection() # Get the collection for testing
    
    print("\n--- Testing add_documents ---")
    artigo1 = get_wikipedia_article("Machine Learning")
    artigo2 = get_wikipedia_article("Artificial Intelligence")
    artigo3 = get_wikipedia_article("Computer Science")
    
    docs_to_add = []
    if artigo1 and artigo1['content'].strip(): docs_to_add.append(artigo1)
    if artigo2 and artigo2['content'].strip(): docs_to_add.append(artigo2)
    if artigo3 and artigo3['content'].strip(): docs_to_add.append(artigo3)

    if docs_to_add:
        add_documents(test_collection, docs_to_add) # Pass test_collection here
    else:
        print("--- No articles fetched for testing add_documents.")

    print("\n--- Testing search_similar ---")
    if test_collection.count() > 0:
        resultado = search_similar(test_collection, "Como as máquinas aprendem?", top_k=2) # Pass test_collection here
        print("\n--- Resultados mais relevantes:")
        if resultado and resultado['documents'] and resultado['documents'][0]:
            for i in range(len(resultado["documents"][0])):
                title = resultado['metadatas'][0][i].get('title', 'N/A')
                content_snippet = resultado['documents'][0][i][:200] + "..." if len(resultado['documents'][0][i]) > 200 else resultado['documents'][0][i]
                print(f"\n--- {title}\nContent Snippet: {content_snippet}")
        else:
            print("--- No search results found.")
    else:
        print("--- Cannot test search_similar: collection is empty after adding.")