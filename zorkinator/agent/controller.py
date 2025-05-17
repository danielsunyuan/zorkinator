import logging
import json
import os

class AgentController:
    def __init__(self, config, runner, llm_client):
        self.config = config
        self.runner = runner
        self.llm_client = llm_client
        self.history = []

    def run(self):
        turns = self.runner.turn_stream()

        try:
            # 🎬 Initial setup
            first_turn = next(turns)
            env_state = self._extract_observation(first_turn)
            observation = self._format_observation(env_state)

            print("\n🧙 Zork says:\n" + observation + "\n")
            logging.info("📥 ZORK INIT: %s", json.dumps(first_turn))

            while True:
                # 🧠 Format prompt for LLM
                prompt = self.build_prompt(observation)

                # 🤖 Get LLM's command
                response = self.llm_client.chat_completion(
                    messages=[
                        {"role": "system", "content": "You are an agent exploring an environment. Respond with a single command."},
                        {"role": "user", "content": prompt}
                    ]
                )

                # Seperator for readability
                print("----------------------------------\n")

                print("🤖 Agent:", response, "\n")
                logging.info("🎤 AGENT RESPONSE: %s", response)

                # 🪝 Step in game with agent's action
                step_feedback = self.runner.send_command(response)
                next_turn = next(turns)
                env_state = self._extract_observation(next_turn)

                # 🧩 Format combined feedback + environment for next step
                observation = self._format_observation(env_state, step_feedback)

                print("🧙 Zork says:\n" + observation + "\n")
                logging.info("🔁 ZORK TURN: %s", json.dumps({
                    "step_result": step_feedback,
                    "env_state": next_turn
                }))

                # 🧾 Track history
                self.history.append((observation, response, observation))

        except (KeyboardInterrupt, StopIteration):
            print("\n👋 Session ended.")
            self.runner.process.terminate()

    def build_prompt(self, game_text):
        return (
            "You are playing Zork.\n"
            "Based on the current game state below, respond with a single concise action.\n\n"
            f"{game_text.strip()}\n"
        )

    def _extract_observation(self, turn):
        if isinstance(turn, dict) and "observation" in turn:
            return turn["observation"]
        return str(turn)

    def _format_observation(self, env_state, step_feedback=None):
        lines = env_state.strip().splitlines()
        location = lines[0] if lines else "Unknown"
        description = "\n".join(lines[1:]) if len(lines) > 1 else ""

        result = (
            f"📍 Location: {location}\n\n"
            f"🌳 Environment:\n{description.strip()}"
        )

        if step_feedback:
            result += f"\n\n🎯 Last Action Result:\n{step_feedback.strip()}"

        return result
