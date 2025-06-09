from typing import Protocol, List
from utils.ollama import OllamaClient

# ──────────────────────────────────────────────────────────────────────
# Reflector interface and implementations
# ──────────────────────────────────────────────────────────────────────
class Reflector(Protocol):
    """
    Generates a reflection string given the transcript and the latest reward.
    """
    def reflect(self, transcript: List[str], reward: int) -> str:
        ...

class NullReflector:
    """
    A no-op reflector that always returns an empty string.
    """
    def reflect(self, transcript: List[str], reward: int) -> str:
        return ""

class LLMReflector:
    """
    Uses an LLM to summarize recent events and the reward into a concise reflection.
    """
    def __init__(self, client: OllamaClient, system_prompt: str = None, history_size: int = 10):
        self.client = client
        self.system_prompt = system_prompt or (
            "You are an assistant that reflects on an agent's gameplay. "
            "Given the recent transcript and the reward received, provide 1-2 insightful sentences."
        )
        self.history_size = history_size

    def reflect(self, transcript: List[str], reward: int) -> str:
        # take last N lines for context
        snippet = "\n".join(transcript[-self.history_size:])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Recent transcript:\n{snippet}\n"  
            f"Recent reward: {reward}\n\n"
            "Reflection:"
        )
        response = self.client.complete(prompt)
        # return first paragraph of response
        return response.strip().split("\n\n")[0]