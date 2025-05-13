import argparse
import yaml
from agent.factory import load_agent_from_config

def main():
    parser = argparse.ArgumentParser(description="Run Zorkinator agent.")
    parser.add_argument("--config", "-c", required=True, help="Path to behaviour config YAML file.")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    agent = load_agent_from_config(config)
    agent.run()

if __name__ == "__main__":
    main()