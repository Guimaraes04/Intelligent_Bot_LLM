from wiki_scraper import get_relevant_articles
from ollama_client import query_ollama, test_ollama_connection
import re
import sys

knowledge_base = []


def build_knowledge_base(question: str):

    global knowledge_base

    print(f"📥 Downloading articles from Wikipedia for: '{question}'")
    knowledge_base = []

    try:
        articles = get_relevant_articles(question, max_articles=5)
        for article in articles:
            knowledge_base.append(article)
            print(f"  ✅ {article['title']} - {len(article['content'])} characters")
    except Exception as e:
        print(f"  ❌ Error downloading articles: {e}")

    print(f"\n📚 Knowledge base built with {len(knowledge_base)} articles.")


def simple_search(query, max_results=2):

    if not knowledge_base:
        return []

    query_words = re.findall(r'\w+', query.lower())
    results = []

    for article in knowledge_base:
        title = article["title"].lower()
        content = article["content"].lower()

        score = 0
        for word in query_words:
            if word in title:
                score += 3
            if word in content:
                score += content.count(word)

        if score > 0:
            results.append({
                "article": article,
                "score": score
            })

    # Sort by relevance and return the best results
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["article"] for r in results[:max_results]]


def answer_question(question: str):

    relevant_articles = simple_search(question)

    if relevant_articles:
        print(f"📖 Found {len(relevant_articles)} relevant articles")

        context_parts = []
        for article in relevant_articles:
            snippet = article["content"][:1000]
            context_parts.append(f"ARTICLE: {article['title']}\n{snippet}")

        context = "\n\n".join(context_parts)

        prompt = f"""You are an intelligent assistant that answers in English.

WIKIPEDIA CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Use the provided context to answer the question.
- If the question is unrelated to the context, answer using general knowledge.
- Always respond in English.
- Be clear and concise.
- If you don't know the answer, say so.

ANSWER:"""

    else:
        # If no relevant articles are found, answer using general knowledge
        print("🧠 No relevant articles found, using general knowledge")

        prompt = f"""You are an intelligent assistant that answers in English.

QUESTION: {question}

INSTRUCTIONS:
- Always respond in English.
- Be clear and concise.
- If you don't know the answer, say so.
- Use your general knowledge.

ANSWER:"""

    print("🤖 Generating the answer...")
    answer = query_ollama(prompt)
    print("\n🤖 AI Response:\n")
    print(answer)


def interactive_mode():

    print("\n💬 Interactive mode started. Type 'exit' to quit.")

    while True:
        try:
            user_question = input("\n🔹 Ask your question: ").strip()

            if user_question.lower() in ['exit', 'quit', '']:
                print("👋 Goodbye!")
                break

            print("\n🔧 Building knowledge base...")
            build_knowledge_base(user_question)

            answer_question(user_question)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🔧 1. Checking connection to Ollama")
    if not test_ollama_connection():
        print("❌ Connection issue with Ollama. Ensure it is running.")
        sys.exit(1)

    print("\n🔧 2. Choose mode:")
    print("  [1] Single question")
    print("  [2] Interactive mode")

    try:
        choice = input("Choose (1 or 2): ").strip()

        if choice == "2":
            interactive_mode()
        else:
            print("\n💬 Ask a question")
            user_question = input("Enter your question: ")
            print("\n🔧 Building knowledge base...")
            build_knowledge_base(user_question)
            answer_question(user_question)
    except KeyboardInterrupt:
        print("\n👋 Program interrupted by user!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")