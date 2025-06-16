from wiki_scraper import get_wikipedia_article
from ollama_client import query_ollama, test_ollama_connection
import re
import sys

# Armazena os artigos em memória (sem ChromaDB)
knowledge_base = []


def build_knowledge_base():
    """Constrói a base de conhecimento usando Wikipedia."""
    global knowledge_base

    termos = [
        "Inteligência artificial",
        "Aprendizado de máquina",
        "Redes neurais artificiais",
        "Processamento de linguagem natural",
        "Deep learning",
        "Machine learning"
    ]

    print("📥 Baixando artigos da Wikipedia...")
    knowledge_base = []

    for termo in termos:
        try:
            print(f"  📄 Baixando: {termo}")
            artigo = get_wikipedia_article(termo)
            if artigo["content"].strip():
                knowledge_base.append(artigo)
                print(f"  ✅ {artigo['title']} - {len(artigo['content'])} caracteres")
            else:
                print(f"  ⚠️ {termo} - conteúdo vazio")
        except Exception as e:
            print(f"  ❌ Erro ao baixar {termo}: {e}")

    print(f"\n📚 Base de conhecimento construída com {len(knowledge_base)} artigos.")


def simple_search(query, max_results=2):
    """Busca simples por palavras-chave nos artigos."""
    if not knowledge_base:
        return []

    query_words = re.findall(r'\w+', query.lower())
    results = []

    for article in knowledge_base:
        title = article["title"].lower()
        content = article["content"].lower()

        # Conta quantas palavras da query aparecem no artigo
        score = 0
        for word in query_words:
            if word in title:
                score += 3  # Palavras no título têm mais peso
            if word in content:
                score += content.count(word)

        if score > 0:
            results.append({
                "article": article,
                "score": score
            })

    # Ordena por relevância e retorna os melhores
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["article"] for r in results[:max_results]]


def answer_question(question: str):
    """Responde usando Wikipedia quando relevante, senão usa conhecimento geral."""

    # Busca na base de conhecimento
    relevant_articles = simple_search(question)

    if relevant_articles:
        # Se encontrou artigos relevantes, usa-os como contexto
        print(f"📖 Encontrados {len(relevant_articles)} artigos relevantes")

        context_parts = []
        for article in relevant_articles:
            # Usa apenas os primeiros 1000 caracteres de cada artigo
            snippet = article["content"][:1000]
            context_parts.append(f"ARTIGO: {article['title']}\n{snippet}")

        context = "\n\n".join(context_parts)

        prompt = f"""Tu és um assistente inteligente que responde em português.

CONTEXTO da Wikipedia:
{context}

PERGUNTA: {question}

INSTRUÇÕES:
- Usa o contexto fornecido para responder à pergunta
- Se a pergunta não estiver relacionada com o contexto, responde com o teu conhecimento geral
- Responde sempre em português
- Sê claro e direto
- Se não souberes a resposta, diz que não sabes

RESPOSTA:"""

    else:
        # Se não encontrou artigos relevantes, responde com conhecimento geral
        print("🧠 Nenhum artigo relevante encontrado, usando conhecimento geral")

        prompt = f"""Tu és um assistente inteligente que responde em português.

PERGUNTA: {question}

INSTRUÇÕES:
- Responde sempre em português
- Sê claro e direto
- Se não souberes a resposta, diz que não sabes
- Usa o teu conhecimento geral

RESPOSTA:"""

    print("🤖 Gerando resposta...")
    answer = query_ollama(prompt)
    print("\n🤖 Resposta da IA:\n")
    print(answer)


def interactive_mode():
    """Modo interativo para fazer múltiplas perguntas."""
    print("\n💬 Modo interativo iniciado. Digite 'sair' para terminar.")

    while True:
        try:
            user_question = input("\n🔹 Faz a tua pergunta: ").strip()

            if user_question.lower() in ['sair', 'exit', 'quit', '']:
                print("👋 Até logo!")
                break

            answer_question(user_question)
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")


if __name__ == "__main__":
    print("🔧 1. Verificar conexão com Ollama")
    if not test_ollama_connection():
        print("❌ Problema de conexão com Ollama. Verifica se está a correr.")
        sys.exit(1)

    print("\n🔧 2. Construir base de conhecimento da Wikipedia")
    try:
        build_knowledge_base()
    except Exception as e:
        print(f"⚠️ Erro ao construir base de conhecimento: {e}")
        print("🔄 Continuando sem Wikipedia...")

    print("\n🔧 3. Escolhe o modo:")
    print("  [1] Uma pergunta")
    print("  [2] Modo interativo")

    try:
        choice = input("Escolha (1 ou 2): ").strip()

        if choice == "2":
            interactive_mode()
        else:
            print("\n💬 Fazer pergunta")
            user_question = input("Escreve a tua pergunta: ")
            answer_question(user_question)
    except KeyboardInterrupt:
        print("\n👋 Programa interrompido pelo utilizador!")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")