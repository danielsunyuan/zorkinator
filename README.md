# Zorkinator

A modular text-adventure agent that uses a **Reason→Act→Observe→Reflect** loop to play classic text-based games like Zork. Built with LangGraph and featuring pluggable components for research on LLM decision-making, automated gameplay, and reward shaping experiments.

## Project Overview

Zorkinator implements a sophisticated agent architecture where:

1. **Reason**: The agent analyzes the current game state and chooses the next action
2. **Act**: The chosen action is executed in the game environment  
3. **Observe**: The agent evaluates the outcome and computes rewards
4. **Reflect**: The agent generates insights about recent gameplay for future reference

**Key Use Cases:**
- Automated text adventure gameplay and completion
- Research on LLM decision-making in interactive environments
- Reward shaping and reinforcement learning experiments
- Ablation studies on different reasoning, evaluation, and reflection strategies

## Architecture

Zorkinator uses a **plugin-based architecture** with three core interfaces that map to LangGraph nodes:

### Plugin Interfaces

- **Reasoner** (`choose_action`): Determines the next action based on current state and environment
- **Evaluator** (`evaluate`): Computes scalar rewards from gameplay transcripts  
- **Reflector** (`reflect`): Generates reflection strings for learning and memory

These components are dynamically loaded and orchestrated through LangGraph's state management system.

### Directory Structure

```
zorkinator/
├── engine/
│   ├── core.py                    # Main engine logic and LangGraph orchestration
│   └── components/
│       ├── reasoners.py           # Action selection strategies
│       ├── evaluators.py          # Reward computation methods  
│       └── reflectors.py          # Reflection generation
├── config/
│   └── zork2.yaml                 # Example configuration
├── config.yaml                    # Main configuration file
├── run.py                         # Entry point and CLI interface
├── utils/
│   └── ollama.py                  # LLM client utilities
├── evaluator/
│   └── post_run.py               # Post-episode analysis
└── jericho/                      # Game files directory
```

## Installation & Requirements

### Dependencies

- **Python 3.11+**
- **Jericho** (text adventure game interface)
- **LangGraph ≥0.0.38** (agent orchestration)
- **LangChain-core** (LLM abstractions)
- **OmegaConf** (configuration management)
- **Ollama** (local LLM server)

### Setup Steps

1. **Create and activate conda environment:**
   ```bash
   conda create -n zorkinator python=3.11 -y
   conda activate zorkinator
   ```

2. **Install system dependencies (for Jericho):**
   ```bash
   sudo apt update
   sudo apt install clang build-essential -y
   ```

3. **Install Python dependencies:**
   ```bash
   export CC=clang
   export CXX=clang++
   pip install --no-binary=jericho -r requirements.txt
   ```

4. **Download game files:**
   ```bash
   bash jericho/download.sh
   ```

5. **Start Ollama server:**
   ```bash
   ollama serve
   ollama pull llama3.1:8b  # or your preferred model
   ```

## Configuration

Zorkinator uses YAML configuration files with the following structure:

```yaml
# config.yaml
game_file: "jericho/games/z-machine-games-master/autoplay-game-suite/zork1.z5"

# Which Reasoner/Evaluator/Reflector to use
reasoner: LLMReasonerNoValids    # options: RandomReasoner, LLMReasoner, LLMReasonerNoValids  
evaluator: LLMEvaluator          # options: NullEvaluator, ScoreDeltaEvaluator, LLMEvaluator
reflector: LLMReflector          # options: NullReflector, LLMReflector

# LLM backend
ollama_model: "llama3.1:8b"
ollama_base_url: "http://localhost:11434"

# Episode settings
episode_max_steps: 1000000
```

### Configuration Overrides

Use `--opts` to override any config value at runtime:

```bash
python run.py -c config.yaml --opts reasoner=RandomReasoner episode_max_steps=100
```

## Basic Usage

### Run a Full Episode

```bash
python run.py -c config.yaml
```

This starts the agent and runs until the game ends or the step limit is reached.

### Run a Single Action

```bash
python run.py -c config.yaml --action "look around"
```

Executes one action in the environment and exits.

### Example Output

```
🚀 Zorkinator modular engine started
> look
West of House
You are standing in an open field west of a white house, with a boarded front door.
There is a small mailbox here.

[Step 1] Phase=reason, Action=look, Reward=0
> north  
You can't go that way.

[Step 2] Phase=act, Action=north, Reward=-1
...
```

## Ablation Testing Guide

**Ablation testing** means systematically varying one component at a time to isolate the effect of each strategy on agent performance.

### Available Components

**Reasoners:**
- `RandomReasoner`: Chooses random actions from common verbs
- `LLMReasoner`: Uses LLM with valid actions context  
- `LLMReasonerNoValids`: Uses LLM without valid actions context

**Evaluators:**  
- `NullEvaluator`: Always returns 0 reward
- `ScoreDeltaEvaluator`: Tracks game score changes
- `LLMEvaluator`: LLM-based reward evaluation

**Reflectors:**
- `NullReflector`: No reflection generation
- `LLMReflector`: LLM-generated gameplay insights

### Sample Experiment Matrix

Create different config files for systematic testing:

```yaml
# config_random_null_null.yaml
reasoner: RandomReasoner
evaluator: NullEvaluator  
reflector: NullReflector

# config_llm_score_llm.yaml
reasoner: LLMReasoner
evaluator: ScoreDeltaEvaluator
reflector: LLMReflector

# config_llm_llm_null.yaml  
reasoner: LLMReasonerNoValids
evaluator: LLMEvaluator
reflector: NullReflector
```

### Running Experiments

```bash
# Test different reasoners (holding evaluator/reflector constant)
python run.py -c config.yaml --opts reasoner=RandomReasoner
python run.py -c config.yaml --opts reasoner=LLMReasoner  
python run.py -c config.yaml --opts reasoner=LLMReasonerNoValids

# Test different evaluators
python run.py -c config.yaml --opts evaluator=NullEvaluator
python run.py -c config.yaml --opts evaluator=ScoreDeltaEvaluator
python run.py -c config.yaml --opts evaluator=LLMEvaluator
```

### Automation Script Example

```bash
#!/bin/bash
reasoners=("RandomReasoner" "LLMReasoner" "LLMReasonerNoValids")
evaluators=("NullEvaluator" "ScoreDeltaEvaluator" "LLMEvaluator")

for r in "${reasoners[@]}"; do
  for e in "${evaluators[@]}"; do
    echo "Testing: $r + $e"
    python run.py -c config.yaml --opts reasoner=$r evaluator=$e episode_max_steps=50 \
      > "results_${r}_${e}.log" 2>&1
  done
done
```

### Key Metrics to Track

- **Total Score**: Final game score achieved
- **Steps to Completion**: Number of actions taken
- **Success Rate**: Percentage of successful game completions
- **Average Reward per Turn**: Mean reward across all actions
- **Unique States Visited**: Exploration effectiveness

## Extending the Engine

### Adding New Components

1. **Create the component class** implementing the appropriate Protocol:

```python
# In engine/components/reasoners.py
class MyCustomReasoner:
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        # Your logic here
        return "custom action"
```

2. **Update your config** to reference the new component:

```yaml
reasoner: MyCustomReasoner
```

3. **Run with your new component** - no code changes to `run.py` required!

```bash
python run.py -c config.yaml
```

The dynamic loader in `run.py` automatically discovers and instantiates your component.

### Component Guidelines

- **Reasoners**: Should handle edge cases gracefully and return valid text adventure commands
- **Evaluators**: Should return integer rewards; consider both immediate and long-term progress  
- **Reflectors**: Should provide concise, actionable insights for future decision-making

## Troubleshooting & Tips

### Common Errors

- **"Connection refused" / Ollama errors**: Ensure `ollama serve` is running and the model is pulled
- **YAML parsing errors**: Check indentation and syntax in config files
- **Import errors**: Verify component names match class names exactly
- **Jericho build failures**: Ensure clang compiler is installed and environment variables are set

### Performance Considerations

- **LLM Call Latency**: Each reasoning step makes an API call; consider faster models for rapid iteration
- **Memory Usage**: Long episodes accumulate large transcript histories
- **Cost Management**: Monitor token usage when using cloud LLM providers
- **Game Complexity**: Start with simpler games (Zork1) before attempting longer adventures

### Debugging Tips

```bash
# Run with verbose output and step limits for debugging
python run.py -c config.yaml --opts episode_max_steps=10

# Test single actions to validate environment setup  
python run.py -c config.yaml --action "inventory"

# Use RandomReasoner to validate basic game mechanics
python run.py -c config.yaml --opts reasoner=RandomReasoner episode_max_steps=5
```

## License & Contributing

This project is open source. To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes following the existing code style
4. Add tests for new components
5. Submit a pull request with a clear description

### Development Setup

```bash
# Install development dependencies
pip install ipykernel matplotlib scipy

# Register Jupyter kernel for notebook development  
python -m ipykernel install --user --name zorkinator --display-name "Python (zorkinator)"
```

---

**Acknowledgments**: This project draws inspiration from text adventure AI research and builds upon the excellent [Jericho](https://github.com/microsoft/jericho) framework for interactive fiction environments.