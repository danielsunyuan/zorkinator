import time
import requests
import json

class ZorkRunner:
    def __init__(self, exec_dir=None, exec_name="zork", base_url="http://jericho:8000", session_id="player1"):
        self.base_url = base_url.rstrip("/")
        self.session_id = session_id
        self.started = False
        self.process = None  # Placeholder for parity with old design

    def start_session(self):
        for _ in range(10):
            try:
                response = requests.post(f"{self.base_url}/start", params={"session_id": self.session_id})
                response.raise_for_status()
                data = response.json()
                return data.get("response", "[No initial description provided]")
            except requests.ConnectionError:
                print("[WARN] Jericho not ready, retrying...")
                time.sleep(2)
        raise RuntimeError("Failed to connect to Jericho after retries.")

    def send_command(self, command):
        payload = {"action": command}
        response = requests.post(
            f"{self.base_url}/step",
            params={"session_id": self.session_id},
            json=payload
        )
        response.raise_for_status()
        return response.json().get("response", "[No response from /step]")

    def get_current_state(self):
        response = requests.get(f"{self.base_url}/state", params={"session_id": self.session_id})
        response.raise_for_status()
        return response.json()["description"]

    def turn_stream(self):
        if not self.started:
            self.started = True
            yield self.start_session()

        while True:
            time.sleep(0.1)
            yield self.get_current_state()

    def end_session(self):
        requests.post(f"{self.base_url}/end", params={"session_id": self.session_id})
