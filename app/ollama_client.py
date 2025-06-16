import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def query_ollama(prompt: str, model="mistral"):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_ctx": 4096  # Increase context window
            }
        }
    )

    if response.status_code != 200:
        print("❌ Erro ao comunicar com o Ollama:", response.text)
        return "Erro ao gerar resposta."

    json_data = response.json()

    if "response" not in json_data:
        print("⚠️ Resposta inesperada do Ollama:", json_data)
        return "Não foi possível obter uma resposta do modelo."

    return json_data["response"]


def test_ollama_connection():
    """Testa a conexão com o Ollama e lista modelos disponíveis."""
    try:
        # Verifica se o Ollama está rodando
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("🟢 Ollama conectado. Modelos disponíveis:")
            for model in models:
                print(f"  - {model['name']}")
            return True
        else:
            print("❌ Ollama não está respondendo corretamente")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao Ollama")
        return False


if __name__ == "__main__":
    # Teste de conexão
    if test_ollama_connection():
        # Teste simples de geração
        test_response = query_ollama("Responde em português: Qual é a capital do Brasil?")
        print(f"\n🧪 Teste de resposta:\n{test_response}")