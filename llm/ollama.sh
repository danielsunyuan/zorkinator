#!/bin/bash

set -e

MODEL="${1:-llama3}"
PORT=11434

# Check if Ollama server is already running
if lsof -i tcp:$PORT | grep LISTEN > /dev/null 2>&1; then
    echo "[✓] Ollama API already running on port $PORT"
else
    echo "[*] Starting Ollama API server..."
    nohup ollama serve > ollama.log 2>&1 &
    sleep 2
    echo "[✓] Ollama API started"
fi

# Preload the model
echo "[*] Preloading model: $MODEL"
ollama run "$MODEL"