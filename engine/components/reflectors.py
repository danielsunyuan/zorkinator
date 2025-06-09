# components/reflectors.py

"""
Reflector module

Purpose:
  Enables Reflexion-style learning by generating natural language
  self-assessments based on the agent's past behavior.

Components:
  - Reflector (interface): defines a reflect() method to produce feedback.
  - NullReflector: no-op placeholder for ablation or disabled mode.
  - LLMReflector: sends the latest transcript and reward to an LLM and
    receives a short verbal reflection to influence future decision-making.

Use Case:
  Called at the end of each episode. Reflections can be stored and prepended
  to the prompt in the next episode to guide future reasoning.
"""

from typing import List
import requests

class Reflector:
    def reflect(self, transcript: List[str], reward: int) -> str:
        raise NotImplementedError

class NullReflector(Reflector):
    def reflect(self, transcript: List[str], reward: int) -> str:
        return ""

class LLMReflector(Reflector):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    def reflect(self, transcript: List[str], reward: int) -> str:
        history = "\n".join(transcript[-20:])
        prompt = (
            f"You are navigating an environment broken down to text.\n"
            f"Here is what happened in the last episode:\n"
            f"{history}\n\n"
            f"You received a reward of {reward}.\n"
            f"Briefly reflect on why that outcome occurred, and what to do differently next time."
        )
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            r = requests.post(f"{self.base_url}/api/generate", json=payload)
            r.raise_for_status()
            return r.json()["response"].strip()
        except Exception as e:
            print(f"[LLMReflector Error] {e}")
            return ""