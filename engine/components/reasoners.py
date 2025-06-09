from typing import Protocol
from jericho import FrotzEnv
from engine.core import AgentState
import random
from utils.ollama import OllamaClient

# ──────────────────────────────────────────────────────────────────────
# 1. Reasoner interface
# ──────────────────────────────────────────────────────────────────────
class Reasoner(Protocol):
    """
    Defines how the agent selects its next action given the current state and environment.
    """
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        ...

# ──────────────────────────────────────────────────────────────────────
# 2. RandomReasoner: simple baseline
# ──────────────────────────────────────────────────────────────────────
class RandomReasoner:
    """
    Chooses randomly from a fixed set of common verbs.
    """
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        return random.choice(["look", "north", "south", "east", "west"])

# ──────────────────────────────────────────────────────────────────────
# 3. LLMReasoner with valid actions context
# ──────────────────────────────────────────────────────────────────────
class LLMReasoner(Reasoner):
    """
    Uses an LLM to pick the next command based on the latest observation,
    and includes valid actions in the prompt.
    """
    def __init__(self, client: OllamaClient, system_prompt: str = None):
        self.client = client
        self.system_prompt = (
            system_prompt
            or "You are an AI agent playing a text-based adventure. Respond with exactly one valid command."
        )

    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        obs = state["obs"]
        # Fetch valid actions for context
        try:
            valid_actions = env.get_valid_actions(use_ctypes=False)
        except Exception:
            valid_actions = []

        valid_text = f"Valid actions: {', '.join(valid_actions)}" if valid_actions else ""
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Observation:\n{obs}\n"
            f"{valid_text}\n\n"
            "Next command:"
        )
        response = self.client.complete(prompt)
        return response.splitlines()[0].strip()

# ──────────────────────────────────────────────────────────────────────
# 4. LLMReasonerNoValids: without valid actions context
# ──────────────────────────────────────────────────────────────────────
class LLMReasonerNoValids(Reasoner):
    """
    Uses an LLM to pick the next command based on the latest observation,
    without fetching valid actions for context.
    """
    def __init__(self, client: OllamaClient, system_prompt: str = None):
        self.client = client
        self.system_prompt = (
            system_prompt
            or "You are an AI agent playing a text-based adventure. Respond with exactly one valid command."
        )

    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        obs = state["obs"]
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Observation:\n{obs}\n\n"
            "Next command:"
        )
        response = self.client.complete(prompt)
        return response.splitlines()[0].strip()