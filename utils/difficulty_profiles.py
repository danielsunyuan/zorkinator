# utils/difficulty_profiles.py
from copy import deepcopy

def apply_difficulty(cfg: dict) -> dict:
    diff = cfg.get("difficulty", "medium").lower()
    out = deepcopy(cfg)

    if diff == "easy":
        out.update({
            "planner": "LLMPlanner",
            "loop_heuristic": "NoLoopHeuristic",
            "include_actions": True,
            "episode_max_steps": None,
            "memory_window": 4000,
        })

    elif diff == "hard":
        out.update({
            "planner": "RandomPlanner",
            "loop_heuristic": "SimpleLoopDetector",
            "include_actions": False,
            "episode_max_steps": 50,
            "memory_window": 1000,
        })

    elif diff == "rogue":
        out.update({
            "planner": "LLMPlanner",
            "loop_heuristic": "SimpleLoopDetector",
            "include_actions": False,
            "episode_max_steps": 200,
            "memory_window": 2000,
            # no reward shaping—agent is “blind”
        })

    else:  # medium (default)
        out.update({
            "planner": "LLMPlanner",
            "loop_heuristic": "SimpleLoopDetector",
            "include_actions": False,
            "episode_max_steps": 200,
            "memory_window": 2000,
        })

    return out