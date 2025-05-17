from agent.controller import AgentController
from api.ollama_client import OllamaClient
from api.zork_runner import ZorkRunner
import yaml

def load_config(path="config.yml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()

    llm = OllamaClient(
        model_name=config["llm_backend"]["model"],
        base_url=config["llm_backend"]["base_url"]
    )

    runner = ZorkRunner(
        exec_dir=config["zork"]["exec_dir"],
        exec_name=config["zork"]["exec_name"]
    )

    agent = AgentController(
        config=config,
        runner=runner,
        llm_client=llm
    )

    agent.run()
