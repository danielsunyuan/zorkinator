# components/map_manager.py

from collections import defaultdict
from typing import Dict, List, Set

class MapManager:
    """
    MapManager tracks the agent's discovered world graph based on visible observations.

    It stores:
    - state transitions: obs_before + action → obs_after
    - untried actions (frontier) per observation
    - optionally, it can infer reverse directions (e.g. north ↔ south)
    """

    REVERSE_DIRECTIONS = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
        "up": "down",
        "down": "up"
    }

    def __init__(self):
        self.graph: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.frontier: Dict[str, Set[str]] = defaultdict(set)

    def record(self, obs_before: str, action: str, obs_after: str):
        """Record a transition from one observation to another via an action."""
        self.graph[obs_before][action] = obs_after
        self.frontier[obs_before].discard(action)

        # Add reverse transition if action is directional
        reverse = self.REVERSE_DIRECTIONS.get(action)
        if reverse:
            self.graph[obs_after][reverse] = obs_before
            self.frontier[obs_after].discard(reverse)

    def add_actions(self, obs: str, actions: List[str]):
        """Add valid actions that have not yet been tried in this observation."""
        known = self.graph.get(obs, {})
        self.frontier[obs].update(a for a in actions if a not in known)

    def get_untried(self, obs: str) -> List[str]:
        """Return list of untried actions in this observation."""
        return list(self.frontier.get(obs, []))

    def get_next_obs(self, obs: str, action: str) -> str:
        """Return the observation that results from this action, if known."""
        return self.graph.get(obs, {}).get(action, "")

    def has_seen(self, obs: str) -> bool:
        return obs in self.graph