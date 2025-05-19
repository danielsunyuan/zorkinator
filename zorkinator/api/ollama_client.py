import requests

class OllamaClient:
    def __init__(self, model_name, base_url, api_key=None):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        print(f"[OllamaClient] Using model: {self.model_name}")

    def chat_completion(self, messages, **kwargs):
        payload = {
            "model": self.model_name,
            "messages": messages,
            **kwargs
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]