# llm/memory.py
from typing import List, Tuple

# A simple in-memory list to store (speaker, text) pairs.
MEMORY: List[Tuple[str, str]] = []

def add_turn(speaker: str, text: str) -> None:
    """
    Add a new turn to the conversation memory.
    :param speaker: Identifier for who is speaking (e.g. "Game", "LLM Reasoning", "LLM Command").
    :param text: The content of what was said.
    """
    MEMORY.append((speaker, text))

def get_memory() -> List[Tuple[str, str]]:
    """Return the entire conversation memory."""
    return MEMORY

def clear_memory() -> None:
    """Clear all conversation memory."""
    global MEMORY
    MEMORY = []

def get_formatted_memory() -> str:
    """
    Return the conversation as a formatted string.
    Each line is formatted as "Speaker: text".
    """
    lines = []
    for speaker, text in MEMORY:
        lines.append(f"{speaker}: {text}")
    return "\n".join(lines)
