import subprocess

class ZorkRunner:
    def __init__(self, zork_path="./zork", zork_dir="zork"):
        self.process = subprocess.Popen(
            zork_path,
            cwd=zork_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
        )

    def send_command(self, cmd: str):
        """Send a command into Zork (must end with newline)."""
        if self.process.stdin:
            self.process.stdin.write(cmd.rstrip() + "\n")
            self.process.stdin.flush()

    def turn_stream(self):
        """Generator yielding each full environment-turn (up to the prompt)."""
        buffer = ""
        try:
            while True:
                char = self.process.stdout.read(1)
                if not char:
                    break
                buffer += char
                # Zork prints '>' at start of a new line to signal prompt
                if buffer.endswith("\n>"):
                    yield buffer.strip()
                    buffer = ""
        finally:
            self.process.terminate()

if __name__ == "__main__":
    runner = ZorkRunner()
    turns = runner.turn_stream()

    # First turn: initial environment
    first = next(turns)
    print("\n--- Turn 1 ---")
    print(first)

    # Example: send a command and capture the next turn
    runner.send_command("go north")
    second = next(turns)
    print("\n--- Turn 2 ---")
    print(second)

    # Clean up
    runner.process.terminate()