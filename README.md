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


# Requriements


Ollama
```
ollama serve
```

Clang Compiler (for Jericho Game Env)
```
sudo apt update
sudo apt install clang build-essential -y
```


# Quickstart


```
conda create -n zorkinator python=3.11 -y
conda activate zorkinator
```

```
# Ensure Jericho builds from source
export CC=clang
export CXX=clang++
pip install --no-binary=jericho -r requirements.txt
```

```
# Download the Libarary of Text Based Games
bash games/download.sh

python -m ipykernel install --user --name zorkinator --display-name "Python (zorkinator)"
```


```
python run.py --difficulty rogue --max-steps 50
```