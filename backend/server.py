from flask import Flask, request, jsonify
from flask_cors import CORS
from main import build_knowledge_base_for_question, answer_question
from ollama_client import test_ollama_connection
import sys
import traceback

app = Flask(__name__)
CORS(app)

# Verifica a ligação ao Ollama ao iniciar o servidor
with app.app_context():
    print("--- Checking connection to Ollama...")
    if not test_ollama_connection():
        print("--- Connection issue with Ollama. Ensure it is running before starting the server.")
        sys.exit(1)
    else:
        print("--- Ollama connection successful.")

@app.route('/ask', methods=['POST'])
def ask_bot():
    """
    Endpoint principal para receber perguntas do frontend.
    Espera um JSON com a chave 'question'.
    """
    data = request.json
    question = data.get('question')

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Constrói a base de conhecimento e obtém artigos relevantes
        collection_obj, knowledge_base_articles = build_knowledge_base_for_question(question)

        # Gera a resposta usando o modelo LLM e a base de conhecimento
        ai_response = answer_question(question, collection_obj, knowledge_base_articles)
        
        return jsonify({"answer": ai_response})
    except Exception as e:
        print(f"--- Server Error: {e}")
        traceback.print_exc()
        return jsonify({"error": f"An internal server error occurred: {str(e)}. Check server logs for details."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')