#!/bin/sh
set -e

# Inicia o servidor em segundo plano
ollama serve &

# Aguarda o servidor estar pronto
sleep 5

# Faz o pull do modelo mistral, se ainda não estiver baixado
ollama pull mistral || true

# Mantém o container vivo
tail -f /dev/null
