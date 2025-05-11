import os
import json
import subprocess

class ZorkRunner:
    def __init__(self, config_path="config/zork_config.json"):
        # Load config
        with open(config_path) as f:
            config = json.load(f)

        zork_path = config.get("zork_path", "./zork")
        zork_dir = config.get("zork_dir", "zork")

        # Validate
        if not os.path.isfile(zork_path):
            raise FileNotFoundError(f"Zork binary not found at {zork_path}")
        if not os.access(zork_path, os.X_OK):
            raise PermissionError(f"Zork binary at {zork_path} is not executable")

        # Launch Zork process
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
                # Zork prompt ends in newline + >
                if buffer.endswith("\n>"):
                    yield buffer.strip()
                    buffer = ""
        finally:
            self.process.terminate()

# ——— Standalone test mode ————————————————————————————————
if __name__ == "__main__":
    runner = ZorkRunner()
    turns = runner.turn_stream()

    print("\n--- Turn 1 ---")
    print(next(turns))

    runner.send_command("go north")
    print("\n--- Turn 2 ---")
    print(next(turns))

    runner.process.terminate()