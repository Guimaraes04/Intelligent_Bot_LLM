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
                "num_ctx": 4096
            }
        }
    )

    if response.status_code != 200:
        print("--- Erro ao comunicar com o Ollama:", response.text)
        return "Erro ao gerar resposta."

    json_data = response.json()

    if "response" not in json_data:
        print("--- Resposta inesperada do Ollama:", json_data)
        return "Não foi possível obter uma resposta do modelo."

    return json_data["response"]


def test_ollama_connection():
    """
    Testa a conexão com o Ollama e lista modelos disponíveis
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            print("--- Ollama conectado. Modelos disponíveis:")
            for model in models:
                print(f"--- - {model['name']}")
            return True
        else:
            print("--- Ollama não está a responder corretamente")
            return False
    except requests.exceptions.ConnectionError:
        print("--- Não foi possível conectar ao Ollama")
        return False


if __name__ == "__main__":
    if test_ollama_connection():
        print("\n--- Testando uma consulta simples:")
        test_prompt = "Qual é a capital de Portugal?"
        response = query_ollama(test_prompt)
        print(f"\n--- Prompt: {test_prompt}\nResposta: {response}")
    else:
        print("\n--- Falha no teste de conexão ou modelos não encontrados.")
