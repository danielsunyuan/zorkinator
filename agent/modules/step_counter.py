# agent/modules/step_counter.py

class StepCounter:
    def __init__(self, config):
        self.count = config.get("start_at", 0)

    def apply(self, game_text, history, prompt, llm_params):
        self.count += 1
        prompt = f"[Step {self.count}] {prompt}"
        return prompt, llm_params