# llm/token_tracker.py
import tiktoken

class TokenTracker:
    def __init__(self, model_name="gpt-3.5-turbo"):
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.total_tokens = 0

    def count_tokens(self, text: str) -> int:
        """Return the number of tokens for the given text."""
        tokens = self.encoding.encode(text)
        return len(tokens)

    def update(self, text: str) -> int:
        """Count tokens for the provided text, add them to the running total, and return the count."""
        tokens = self.count_tokens(text)
        self.total_tokens += tokens
        return tokens

    def get_total_tokens(self) -> int:
        """Return the total tokens counted so far."""
        return self.total_tokens

# Global instance to be used by other modules
token_tracker = TokenTracker(model_name="gpt-3.5-turbo")
