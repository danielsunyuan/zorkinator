# utils/config_loader.py

from engine.components.planners import LLMPlanner, RandomPlanner
from engine.components.loop_heuristics import SimpleLoopDetector, NoLoopHeuristic
from utils.ollama import OllamaClient


def build_components(config: dict):
    """
    Given a config dictionary, build and return initialized components.
    Returns: (planner, loop_heuristic)
    """
    # Build planner
    if config["planner"] == "LLMPlanner":
        client = OllamaClient(
            model=config.get("ollama_model", "llama3.1:8b"),
            base_url=config.get("ollama_base_url", "http://localhost:11434")
        )
        planner = LLMPlanner(client)
    else:
        planner = RandomPlanner()

    # Build loop heuristic
    if config.get("loop_heuristic") == "SimpleLoopDetector":
        loop = SimpleLoopDetector()
    else:
        loop = NoLoopHeuristic()

    return planner, loop