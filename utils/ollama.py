# utils/ollama.py

import requests

class OllamaClient:
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            print(f"\n[OllamaClient] Prompt sent to model '{self.model}':\n{prompt}\n")
            res = requests.post(f"{self.base_url}/api/generate", json=payload)
            res.raise_for_status()
            response = res.json()["response"].strip()
            print(f"[OllamaClient] Response:\n{response}\n")
            return response
        except Exception as e:
            print(f"[OllamaClient Error] {e}")
            return "look"