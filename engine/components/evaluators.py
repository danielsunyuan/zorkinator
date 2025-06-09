from typing import Protocol, List
from utils.ollama import OllamaClient

# ──────────────────────────────────────────────────────────────────────
# Evaluator interface
# ──────────────────────────────────────────────────────────────────────
class Evaluator(Protocol):
    """
    Computes an integer reward from the transcript of past turns.
    """
    def evaluate(self, transcript: List[str]) -> int:
        ...

# ──────────────────────────────────────────────────────────────────────
# 1. NullEvaluator
# ──────────────────────────────────────────────────────────────────────
class NullEvaluator:
    """
    A no-op evaluator that always returns zero.
    """
    def evaluate(self, transcript: List[str]) -> int:
        return 0

# ──────────────────────────────────────────────────────────────────────
# 2. ScoreDeltaEvaluator (text-based)
# ──────────────────────────────────────────────────────────────────────
class ScoreDeltaEvaluator:
    """
    Parses lines containing 'point(s)' in the transcript to compute the change
    in score since the last evaluation. Works purely on text output.
    """
    def __init__(self):
        self._last_score = 0

    def _extract_score(self, transcript: List[str]) -> int:
        for line in reversed(transcript):
            lower = line.lower()
            if 'point' in lower:
                words = lower.split()
                for i, w in enumerate(words):
                    if w.isdigit() and i+1 < len(words) and 'point' in words[i+1]:
                        return int(w)
        return 0

    def evaluate(self, transcript: List[str]) -> int:
        current = self._extract_score(transcript)
        delta = current - self._last_score
        self._last_score = current
        return delta

# ──────────────────────────────────────────────────────────────────────
# 3. LoopPenaltyEvaluator
# ──────────────────────────────────────────────────────────────────────
class LoopPenaltyEvaluator:
    """
    Penalizes repeating the same observation-action pair.
    Returns -1 if the last pair occurred before; otherwise 0.
    """
    def evaluate(self, transcript: List[str]) -> int:
        # build list of (obs, action) pairs
        pairs = []
        for i in range(len(transcript)-1):
            if transcript[i].startswith('> '):
                action = transcript[i][2:]
                obs = transcript[i+1]
                pairs.append((obs, action))
        if not pairs:
            return 0
        last_pair = pairs[-1]
        # if last_pair appears more than once, it's a loop
        if pairs.count(last_pair) > 1:
            return -1
        return 0

# ──────────────────────────────────────────────────────────────────────
# 4. NoveltyEvaluator
# ──────────────────────────────────────────────────────────────────────
class NoveltyEvaluator:
    """
    Rewards new observations.
    Returns 1 if the last observation is unique in the transcript; otherwise 0.
    """
    def evaluate(self, transcript: List[str]) -> int:
        if not transcript:
            return 0
        last_obs = transcript[-1]
        return 1 if transcript.count(last_obs) == 1 else 0

# ──────────────────────────────────────────────────────────────────────
# 5. KeywordEvaluator
# ──────────────────────────────────────────────────────────────────────
class KeywordEvaluator:
    """
    Rewards presence of any keyword in the last observation.
    """
    def __init__(self, keywords: List[str], reward: int = 1):
        self.keywords = set(k.lower() for k in keywords)
        self.reward = reward

    def evaluate(self, transcript: List[str]) -> int:
        if not transcript:
            return 0
        last_obs = transcript[-1].lower()
        return self.reward if any(k in last_obs for k in self.keywords) else 0

# ──────────────────────────────────────────────────────────────────────
# 6. LLMEvaluator (self-evaluation via LLM)
# ──────────────────────────────────────────────────────────────────────
class LLMEvaluator:
    """
    Uses an LLM to self-evaluate the trajectory. Returns an integer reward.
    Prompts: System instruction + transcript snippet + 'Reward:'.
    """
    def __init__(self, client: OllamaClient, system_prompt: str = None):
        self.client = client
        self.system_prompt = (
            system_prompt or
            'You are an assistant evaluating the success of an agent in a text adventure. '
            'Given the transcript of actions and observations, return a single integer reward between -1 and 1.'
        )

    def evaluate(self, transcript: List[str]) -> int:
        # take last 10 lines for context
        snippet = '\n'.join(transcript[-10:])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"Transcript:\n{snippet}\n\n"
            "Reward:"
        )
        response = self.client.complete(prompt)
        # parse first integer in response
        for line in response.splitlines():
            for token in line.split():
                try:
                    val = int(token)
                    return max(min(val, 1), -1)
                except ValueError:
                    continue
        return 0