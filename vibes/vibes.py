import json
from pathlib import Path

class Vibes:
    def __init__(self, path="vibes/vibes.json"):
        self.path = Path(path)
        self.vibes = self.load()

    def load(self):
        if self.path.exists():
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.vibes, f, indent=2)

    def get(self, scale):
        return self.vibes.get(scale, 0.5)

    def set(self, scale, value):
        self.vibes[scale] = max(0.0, min(1.0, value))  # Clamp to [0.0, 1.0]
        self.save()

    def invert(self, scale):
        if scale in self.vibes:
            self.vibes[scale] = 1.0 - self.vibes[scale]
            self.save()

    def summary(self):
        return {
            "overall_mood": self.calculate_overall_mood()
        }

    def calculate_overall_mood(self):
        # Example composite: lower is more positive
        mood_axes = ["happy_sad", "calm_angry", "confident_afraid"]
        if not all(axis in self.vibes for axis in mood_axes):
            return "neutral"
        score = sum(self.vibes[axis] for axis in mood_axes) / len(mood_axes)
        if score < 0.3:
            return "positive"
        elif score > 0.7:
            return "negative"
        return "neutral"