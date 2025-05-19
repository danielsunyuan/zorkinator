#!/bin/bash
set -e

echo "▶ Starting Ollama server..."
ollama serve &

echo "⏳ Waiting for Ollama server to be ready..."
until ollama list > /dev/null 2>&1; do
  echo "… server not ready"
  sleep 1
done

echo "✅ Pulling model: $OLLAMA_MODEL"
ollama pull "$OLLAMA_MODEL"

echo "📡 Server ready and model pulled. Holding open..."
tail -f /dev/null
