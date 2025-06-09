# components/evaluators.py

from typing import List

class Evaluator:
    def evaluate(self, transcript: List[str]) -> int:
        raise NotImplementedError

class NullEvaluator(Evaluator):
    def evaluate(self, transcript: List[str]) -> int:
        return 0  # Neutral feedback

class ScoreDeltaEvaluator(Evaluator):
    def __init__(self, env):
        self.env = env
        self.last_score = env.get_score()

    def evaluate(self, transcript: List[str]) -> int:
        current_score = self.env.get_score()
        delta = current_score - self.last_score
        self.last_score = current_score
        if delta > 0:
            return 1
        elif delta < 0:
            return -1
        return 0