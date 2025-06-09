# evaluator/post_run.py
from typing import List, Dict, Any


def _unique_rooms(transcript: List[str]) -> int:
    """Count distinct first lines of each observation."""
    return len({obs.splitlines()[0] for obs in transcript}) if transcript else 0


def _unique_verbs(transcript: List[str]) -> int:
    """Very rough heuristic: count distinct first words after '> '."""
    verbs = set()
    for line in transcript:
        if line.startswith("> "):
            verbs.add(line[2:].split()[0].lower())
    return len(verbs)


def evaluate_run(env, transcript: List[str], done: bool = False) -> Dict[str, Any]:
    """
    Post-hoc analysis of an episode.

    Args
    ----
    env : jericho.FrotzEnv
    transcript : List[str]   Full text log (we assume you already prepended obs & actions)
    done : bool              Whether the game reached a terminal state

    Returns
    -------
    dict  Rich evaluation summary
    """
    score = env.get_score()
    max_score = getattr(env, "get_max_score", lambda: None)()
    moves = env.get_moves()

    summary = {
        "final_score": score,
        "max_score": max_score,
        "score_pct": round(score / max_score, 3) if max_score else None,
        "moves": moves,
        "game_done": done,
        "steps_in_loop": len(transcript),
        "unique_rooms": _unique_rooms(transcript),
        "unique_verbs": _unique_verbs(transcript),
        "last_obs": transcript[-1] if transcript else None,
    }

    return summary