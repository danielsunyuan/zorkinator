import logging
import importlib

def load_pipeline(config):
    modules = []
    for entry in config.get("pipeline", []):
        name = entry["name"]
        mod = importlib.import_module(f"agent.modules.{name}")
        cls = getattr(mod, name[0].upper() + name[1:])  # StepCounter
        instance = cls(entry.get("config", {}))
        modules.append(instance)
    return modules

class Agent:
    def __init__(self, config, runner, llm_client):
        self.config = config
        self.runner = runner
        self.llm_client = llm_client
        self.history = []

    def run(self):
        turns = self.runner.turn_stream()

        try:
            first_turn = next(turns)
            print("\n🧙 Zork:\n" + first_turn + "\n")
            logging.info("ZORK: %s", first_turn)

            while True:
                prompt = self.build_prompt(first_turn)
                response = self.llm_client.chat_completion(
                    messages=[
                        {"role": "system", "content": "You are an agent exploring an environment. Respond with a single command."},
                        {"role": "user", "content": prompt}
                    ]
                )

                print("🤖 Agent:", response, "\n")
                logging.info("AGENT: %s", response)

                self.runner.send_command(response)
                next_turn = next(turns)

                print("🧙 Zork:\n" + next_turn + "\n")
                logging.info("ZORK: %s", next_turn)

                self.history.append((first_turn, response, next_turn))
                first_turn = next_turn

        except (KeyboardInterrupt, StopIteration):
            print("\n👋 Session ended.")
            self.runner.process.terminate()

    def build_prompt(self, game_text):
        return (
            f"You are playing Zork. The current game state is:\n\n{game_text}\n\n"
            "Respond with a single concise action."
        )