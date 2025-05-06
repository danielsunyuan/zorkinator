# Zorkinator

An AI-powered assistant that plays the classic text adventure game Zork.

## Overview

Zorkinator uses Large Language Models (LLMs) to play Zork, a classic text adventure game from the 1980s. It interfaces with the original Zork game binary and uses an LLM to generate commands, providing an interesting demonstration of AI problem-solving in a text-based environment.

## Features

- Play Zork with AI assistance using either OpenAI or Ollama models
- Track token usage for LLM calls
- Option to dump conversation history
- Basic map visualization
- Flexible configuration options

## Installation
https://github.com/devshane/zork
### Prerequisites

- Python 3.9+
- Conda (recommended for environment management)
- Ollama (optional, for running local LLMs)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/zorkinator.git
   cd zorkinator
   ```

2. Create and activate a conda environment:
   ```bash
   conda create -n zorkinator python=3.11 -y
   conda activate zorkinator
   ```

3. Install dependencies:
   ```bash
   pip install langchain langchain-community langchain-core langchain-openai langchain-ollama tiktoken
   ```

4. If you want to use Ollama, [install it](https://ollama.ai/download) and download a model:
   ```bash
   ollama pull llama3
   ```

## Usage

### Running with OpenAI (requires API key)

1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

2. Run Zorkinator:
   ```bash
   python zorkinator.py
   ```

### Running with Ollama (local models, no API key needed)

1. Start the Ollama server in a separate terminal:
   ```bash
   ollama serve
   ```

2. Run Zorkinator with Ollama:
   ```bash
   python zorkinator.py --use-ollama --ollama-model=llama3
   ```

### Command-line Options

Zorkinator supports several command-line options:

- `--use-ollama`: Use Ollama instead of OpenAI API
- `--ollama-model=MODEL_NAME`: Specify the Ollama model to use (default: llama2)
- `--token`: Enable token debug output
- `--dump-history`: Dump conversation history to a file (default: conversation_history.txt)
- `--show-map`: Show a text-based map visualization
- `--visual-map`: Show a graphical map visualization (requires additional dependencies)

### Examples

Run with Ollama using the llama3 model and show token usage:
```bash
python zorkinator.py --use-ollama --ollama-model=llama3 --token
```

Run with OpenAI and show the map:
```bash
python zorkinator.py --show-map
```

## Troubleshooting

### Common Issues

1. **Ollama connection errors**:
   - Ensure the Ollama server is running with `ollama serve`
   - Check that you have pulled the model you're trying to use

2. **OpenAI API errors**:
   - Verify your API key is set correctly
   - Check your OpenAI account has sufficient credits

3. **Module not found errors**:
   - Ensure all dependencies are installed in your environment
   - Make sure you've activated the conda environment

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.




ollama-agent/
├── client/
│   └── ollama_client.py       # Your wrapper class around OpenAI for Ollama
│
├── config/
│   └── default.json           # Config for model, base_url, etc.
│
├── main.py                    # Script that runs Agent with OllamaClient
├── ollama.sh                  # Script to start Ollama serve + preload model