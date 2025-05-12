import json
from openai import OpenAI

def load_params(path="config/params.json"):
    with open(path) as f:
        return json.load(f)

class OllamaClient(OpenAI):
    def __init__(self, config_path="config/model_config.json", **overrides):
        # Load config from JSON file
        with open(config_path) as f:
            config = json.load(f)

        # Set model name from override or config
        self.model_name = overrides.get("model_name") or config.get("model_name")
        if not self.model_name:
            raise ValueError("Model name must be provided via config or override.")

        # Setup kwargs for OpenAI client
        kwargs = {
            "base_url": config.get("base_url"),
            "api_key": config.get("api_key"),
            **overrides,
        }

        super().__init__(**kwargs)
        print(f"[OllamaClient] Using model: {self.model_name}")

    def chat_completion(self, messages, **kwargs):
        kwargs.setdefault("model", self.model_name)
        return self.chat.completions.create(messages=messages, **kwargs)