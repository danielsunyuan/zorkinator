# main.py
import logging
from client.ollama_client import OllamaClient
from zork_runner import ZorkRunner

LOG_FILE = "zork_game.log"

# ——— Configure logging —————————————————————————————————————————————
logging.basicConfig(
    filename=LOG_FILE,
    filemode="w",            # overwrite each run
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

def get_agent_move(client, convo):
    """
    Ask Ollama for the next move, given the full conversation so far.
    Expects `convo` to be a list of messages in {role,content} format.
    Returns a single-line Zork command.
    """
    stream = client.chat.completions.create(
        model=client.model_name,
        messages=convo,
        stream=True
    )

    suggestion = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            suggestion += delta

    # only keep up to the first newline
    return suggestion.strip().split("\n")[0]

def main():
    client = OllamaClient(config_path="config/model_config.json")
    runner = ZorkRunner(config_path="config/zork_config.json")
    turns = runner.turn_stream()

    # ——— initialize conversation history ——————————————————————
    convo = [
        {
            "role": "system",
            "content": (
                "You are an agent exploring an environment. "
                "Based on the environments narration, you output exactly one concise action compatible with the environment."
            )
        }
    ]

    try:
        # ——— First turn (game intro) —————————————————————————
        first_turn = next(turns)
        print("\n🧙 Zork:\n" + first_turn + "\n")
        logging.info("ZORK: %s", first_turn)

        # add player’s “what do I do?” prompt for the agent
        convo.append({
            "role": "user",
            "content": (
                f"In Zork, the game just said:\n\n{first_turn}\n\n"
                "What should I do next? (Just the single action)"
            )
        })

        # ——— Main loop —————————————————————————————————————
        while True:
            # 1. Ask the agent for its move
            move = get_agent_move(client, convo)
            print("🤖 Agent plays:", move, "\n")
            logging.info("AGENT: %s", move)

            # 2. Record the agent’s reply in the convo history
            convo.append({"role": "assistant", "content": move})

            # 3. Send that move into Zork
            runner.send_command(move)

            # 4. Read the next turn from Zork
            next_turn = next(turns)
            print("🧙 Zork:\n" + next_turn + "\n")
            logging.info("ZORK: %s", next_turn)

            # 5. Ask agent again based on this new state
            convo.append({
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
        print(f"\nSession log written to {LOG_FILE}")

if __name__ == "__main__":
    main()