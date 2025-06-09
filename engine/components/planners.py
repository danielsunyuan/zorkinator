# components/planners.py

"""
Planner module

Purpose:
  Defines the agent's policy: how it selects actions given observations.

Components:
  - Planner (interface): all planners implement choose_action().
  - RandomPlanner: picks from a fixed list of common verbs.
  - LLMPlanner: uses an LLM (via OllamaClient) to choose the next action
    based on the current observation, using natural language prompts.

Use Case:
  Plug into the engine's think() step to decide what the agent should do next.
  Supports clean experimentation and ablation across reasoning strategies.
"""

from typing import List
from jericho import FrotzEnv
from engine.core import AgentState
import random
from utils.ollama import OllamaClient

class Planner:
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        raise NotImplementedError

class RandomPlanner(Planner):
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        return random.choice(["look", "north", "south", "east", "west"])

class LLMPlanner(Planner):
    def __init__(self, client: OllamaClient, system_prompt: str = None):
        self.client = client
        self.system_prompt = system_prompt or (
            "You are an agent playing a classic text-based game like Zork.\n"
            "Respond only with ONE valid command per turn, like:\n"
            "Do NOT explain. Do NOT speak in full sentences."
        )

    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        obs = state["obs"]

        try:
            valid_actions = env.get_valid_actions(use_ctypes=False, use_parallel=False)
        except Exception as e:
            print(f"[LLMPlanner Warning] Failed to fetch valid actions: {e}")
            valid_actions = []

        actions_text = f"\nValid actions: {', '.join(valid_actions)}" if valid_actions else ""
        prompt = f"{self.system_prompt}\n\nObservation:\n{obs}{actions_text}"

        response = self.client.complete(prompt)
        return response.split("\n")[0].strip()