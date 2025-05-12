# main.py
import logging
from client.ollama_client import OllamaClient
from zork_runner import ZorkRunner
from agent import Agent
import argparse
import yaml
import os

LOG_FILE = "zork.log"

# ——— Configure logging —————————————————————————————————————————————
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",            # overwrite each run
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

def load_behaviour_config(config_name):
    path = os.path.join("behaviours", config_name)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Run Zorkinator with specified behaviour config.")
    parser.add_argument("--behaviour", required=True, help="Path to the behaviour YAML file.")
    args = parser.parse_args()

    behaviour_config = load_behaviour_config(args.behaviour)

    client = OllamaClient(
        model_name=behaviour_config["llm_backend"]["model"],
        base_url=behaviour_config["llm_backend"]["base_url"],
        api_key=behaviour_config["llm_backend"].get("api_key")
    )
    runner = ZorkRunner(config_path="config/zork_config.json")

    agent = Agent(config=behaviour_config)
    agent.run(runner, client)

if __name__ == "__main__":
    main()

# agent.py
import logging
from vibes.vibes import Vibes
from vibes.llm_param_resolver import LLMParamResolver

class Agent:
    def __init__(self, config):
        self.config = config
        self.vibes = Vibes()
        self.resolver = LLMParamResolver(self.vibes.vibes)
        self.convo = [
            {
                "role": "system",
                "content": (
                    "You are an agent exploring an environment. "
                    "Based on the environments narration, you output exactly one concise action compatible with the environment."
                )
            }
        ]

    def get_agent_move(self, client, llm_params):
        stream = client.chat.completions.create(
            model=client.model_name,
            messages=self.convo,
            stream=True,
            **llm_params
        )
        suggestion = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                suggestion += delta
        return suggestion.strip().split("\n")[0]

    def run(self, runner, client):
        turns = runner.turn_stream()

        try:
            first_turn = next(turns)
            print("\n🧙 Zork:\n" + first_turn + "\n")
            logging.info("ZORK: %s", first_turn)

            self.convo.append({
                "role": "user",
                "content": (
                    f"In Zork, the game just said:\n\n{first_turn}\n\n"
                    "What should I do next? (Just the single action)"
                )
            })

            while True:
                llm_params = self.resolver.resolve()
                move = self.get_agent_move(client, llm_params)
                print("🤖 Agent plays:", move, "\n")
                logging.info("AGENT: %s", move)

                self.convo.append({"role": "assistant", "content": move})
                runner.send_command(move)

                next_turn = next(turns)
                print("🧙 Zork:\n" + next_turn + "\n")
                logging.info("ZORK: %s", next_turn)

                self.convo.append({
                    "role": "user",
                    "content": (
                        f"In Zork, the game just said:\n\n{next_turn}\n\n"
                        "What should I do next? (Just the single action)"
                    )
                })

        except KeyboardInterrupt:
            print("\n👋 Exiting on user interrupt.")
        except StopIteration:
            print("👋 Zork process ended.")
        finally:
            runner.process.terminate()
            print("\nSession log written to zork.log")