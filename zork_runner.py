import os
import subprocess

class ZorkRunner:
    def __init__(self, exec_dir: str, exec_name: str = "zork"):
        zork_path = os.path.join(exec_dir, exec_name)

        if not os.path.isfile(zork_path):
            raise FileNotFoundError(f"Zork binary not found at {zork_path}")
        if not os.access(zork_path, os.X_OK):
            raise PermissionError(f"Zork binary at {zork_path} is not executable")

        self.process = subprocess.Popen(
            f"./{exec_name}",
            cwd=exec_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,
        )

    def send_command(self, cmd: str):
        if self.process.stdin:
            self.process.stdin.write(cmd.rstrip() + "\n")
            self.process.stdin.flush()

    def turn_stream(self):
        buffer = ""
        try:
            while True:
                char = self.process.stdout.read(1)
                if not char:
                    break
                buffer += char
                if buffer.endswith("\n>"):
                    yield buffer.strip()
                    buffer = ""
        finally:
            self.process.terminate()