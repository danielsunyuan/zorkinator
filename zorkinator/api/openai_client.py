# api/openai_client.py
import os
import openai

class OpenAIClient:
    def __init__(self, model_name, api_key=None):
        self.model_name = model_name
        openai.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("Must provide OPENAI_API_KEY env var or api_key arg")
        print(f"[OpenAIClient] Using model: {self.model_name}")

    def chat_completion(self, messages, **kwargs):
        """
        messages: list of {"role": "...", "content": "..."}
        kwargs can include temperature, max_tokens, etc.
        """
        resp = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        )
        return resp.choices[0].message.content