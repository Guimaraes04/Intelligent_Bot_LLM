from wiki_scraper import get_relevant_articles
from ollama_client import query_ollama
from vector_store import get_or_reset_wiki_collection, add_documents, search_similar

def build_knowledge_base_for_question(question: str):
    """
    Downloads relevant articles from Wikipedia, adds them to the vector store.
    Returns the collection object and the list of articles added.
    """
    collection = get_or_reset_wiki_collection()
    print(f"--- Downloading articles from Wikipedia for: '{question}'")
    articles_data = []

    try:
        articles = get_relevant_articles(question, max_articles=5)
        if not articles:
            print("--- No relevant articles found on Wikipedia.")
            return collection, []

        for article in articles:
            if article["content"].strip():
                articles_data.append(article)
                print(f"--- {article['title']} - {len(article['content'])} characters")
            else:
                print(f"--- Skipping empty article: {article['title']}")

        if articles_data:
            add_documents(collection, articles_data)
            print(f"--- Knowledge base built with {len(articles_data)} articles in vector store.")
        else:
            print("--- No articles were suitable for the knowledge base.")

    except Exception as e:
        print(f"--- Error downloading or adding articles to vector store: {e}")

    return collection, articles_data

def answer_question(question: str, collection, knowledge_base_articles: list[dict]):
    """
    Generates an answer to the question using Ollama,
    leveraging the knowledge base.
    Returns the generated answer string.
    """
    context = ""

    if knowledge_base_articles:
        # Pesquisa vetorial para encontrar partes mais relevantes da base de conhecimento
        relevant_docs = search_similar(collection, question, top_k=2)

        if (relevant_docs and relevant_docs['documents'] and 
            relevant_docs['documents'][0]):
            print("\n--- Found relevant context from vector store:")
            for i, doc_content in enumerate(relevant_docs['documents'][0]):
                title = relevant_docs['metadatas'][0][i].get('title', 'Unknown Title')
                context += f"Article Title: {title}\nArticle Content: {doc_content}\n\n"
                print(f"--- - {title}")
        else:
            print("\n--- No highly relevant documents found in vector store for the query.")
            context = "No specific articles found to provide context. Based on general knowledge:\n"
    else:
        print("\n--- Knowledge base is empty. Answering based on general model knowledge.")
        context = "No specific articles found to provide context. Based on general knowledge:\n"

    if not context.strip():
        prompt = f"Question: {question}\nAnswer:"
    else:
        # Trunca o contexto se for demasiado longo para o modelo
        max_context_length = 3000
        if len(context) > max_context_length:
            context = context[:max_context_length] + "..."
            print(f"--- Context truncated to {max_context_length} characters.")

        prompt = (
            f"Context: {context}\n"
            f"Question: {question}\n"
            "Based on the provided context, answer the question comprehensively. "
            "If the information is not in the context, state that and try to answer from general knowledge.\n"
            "Answer:"
        )

    print("\n--- Querying Ollama...")
    answer = query_ollama(prompt)

    print("\n--- AI Response:\n")
    print(answer)

    return answer