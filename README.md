# Zorkinator

An AI that plays Zork, utilizing a small parameter LLM with fine-tuned macro controls in real-time API calls.

## What is Zorkinator?

Zorkinator connects a local LLM (via Ollama) to the classic text adventure game Zork. The AI agent receives the game state and generates appropriate commands to progress through the game.

## Key Features

- Uses local Ollama models for LLM inference
- Real-time API communication with the Zork game
- Configurable model parameters via JSON config files
- Simple interface that connects LLM responses to game inputs

## Quick Start

1. Ensure Ollama is installed and running:
   ```bash
   ./ollama.sh
   ```

2. Run Zorkinator:
   ```bash
   python main.py
   ```

## Configuration

Edit the config files in the `config/` directory to customize:
- Model selection (`model_config.json`)
- LLM parameters (`params.json`)
- Game-specific settings (`zork_config.json`)

## Requirements

- Python 3.9+
- Ollama with llama3 model
- Zork game binary

## Thank You

Like samples in a hip-hop track, this project draws inspiration from:
- https://github.com/bburns/Lantern.git
- https://github.com/devshane/zork.git



conda create -n jericho python=3.11 -y
export CC=clang CXX=clang++
python -m pip install --no-binary :all: jericho==3.3.0
python -m pip install spacy
python -m spacy download en_core_web_sm