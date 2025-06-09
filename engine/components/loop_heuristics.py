# components/loop_heuristics.py

"""
LoopHeuristic module

Purpose:
  Detect and mitigate looping behavior in agent trajectories.

Components:
  - LoopHeuristic (interface): defines an avoid_loop() method.
  - NoLoopHeuristic: does nothing; always returns the original action.
  - SimpleLoopDetector: tracks a sliding window of (obs, action) pairs
    and overrides the action if a known loop is detected.

Use Case:
  Prevents the agent from repeating the same ineffective behavior over and over,
  by identifying repeated sequences and optionally replacing the chosen action
  with a fallback (e.g. exploration verb).
"""

from collections import deque
from engine.engine_core import AgentState
from typing import Set
import random

class LoopHeuristic:
    def avoid_loop(self, state: AgentState, action: str) -> str:
        raise NotImplementedError

class NoLoopHeuristic(LoopHeuristic):
    def avoid_loop(self, state: AgentState, action: str) -> str:
        return action

class SimpleLoopDetector(LoopHeuristic):
    def __init__(self, window: int = 5):
        self.window = window
        self.history = deque(maxlen=window)
        self.seen_loops: Set[tuple] = set()

    def avoid_loop(self, state: AgentState, action: str) -> str:
        obs = state["obs"]
        self.history.append((obs, action))
        if len(self.history) == self.window:
            loop_key = tuple(self.history)
            if loop_key in self.seen_loops:
                fallback = ["north", "south", "east", "west", "look"]
                return random.choice(fallback)
            self.seen_loops.add(loop_key)
        return action