# main.py
import sys
from client.ollama_client import OllamaClient
from zork_runner import ZorkRunner

ZORK_PATH = "./zork"
ZORK_DIR  = "zork"

def get_agent_move(client, turn_text):
    """
    Send the current turn_text to the Ollama agent and return
    the single-sentence move it suggests.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful narrator who explains what is happening in the game Zork "
                "and then tells the player exactly one concise next move (1–2 sentences)."
            )
        },
        {"role": "user", "content": f"In Zork, the game just said:\n\n{turn_text}\n\nWhat should I do next?"}
    ]

    stream = client.chat.completions.create(
        model=client.model_name,
        messages=messages,
        stream=True
    )

    # accumulate the content deltas into one string
    suggestion = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            suggestion += delta

    # strip off anything after a newline (we only want the first sentence)
    return suggestion.strip().split("\n")[0]

def main():
    client = OllamaClient()
    runner = ZorkRunner(zork_path=ZORK_PATH, zork_dir=ZORK_DIR)
    turns = runner.turn_stream()

    try:
        # Get and display the very first turn
        first_turn = next(turns)
        print("\n🧙 Zork:\n" + first_turn + "\n")

        # Loop: ask agent for move, send it, print next turn
        while True:
            move = get_agent_move(client, first_turn)
            print("🤖 Agent suggests:", move, "\n")

            runner.send_command(move)
            next_turn = next(turns)
            print("🧙 Zork:\n" + next_turn + "\n")

            first_turn = next_turn  # for the next iteration

    except KeyboardInterrupt:
        print("\n👋 Exiting on user interrupt.")
    except StopIteration:
        print("👋 Zork process ended.")
    finally:
        # ensure we clean up the subprocess
        try:
            runner.process.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()