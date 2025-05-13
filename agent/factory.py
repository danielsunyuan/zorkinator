from agent.base import Agent
from llm.ollama_client import OllamaClient  # Adjust this if using OpenAI
from zork_runner import ZorkRunner

def load_agent_from_config(config):
    # --- LLM Backend Setup ---
    llm_cfg = config["llm_backend"]

    llm_client = OllamaClient(
        model_name=llm_cfg["model"],
        base_url=llm_cfg["base_url"],
        api_key=llm_cfg.get("api_key")
    )

    # --- Zork Game Setup ---
    zork_cfg = config["zork"]

    runner = ZorkRunner(
        exec_dir=zork_cfg["exec_dir"],
        exec_name=zork_cfg.get("exec_name", "zork")
    )

    # --- Agent Setup ---
    return Agent(
        config=config,
        runner=runner,
        llm_client=llm_client
    )