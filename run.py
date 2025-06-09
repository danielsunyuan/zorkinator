#!/usr/bin/env python
import argparse
import importlib
from typing import List, Tuple

from omegaconf import OmegaConf
from utils.ollama import OllamaClient
from evaluator.post_run import evaluate_run
from engine.core import ZorkinatorEngine
from langchain_core.runnables import RunnableConfig


def instantiate_class(path: str, *args, **kwargs):
    """
    Dynamically import and instantiate a class by its full module path.
    Falls back to no-argument constructor on TypeError.
    """
    module_path, cls_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, cls_name)
    try:
        return cls(*args, **kwargs)
    except TypeError:
        return cls()


def run_episode(
    engine: ZorkinatorEngine,
    max_steps: int | None
) -> Tuple[List[str], bool]:
    transcript = [engine.initial_state["obs"]]
    cfg = RunnableConfig(recursion_limit=1_000_000)
    state = engine.initial_state
    steps, done = 0, False

    for state in engine.graph.stream(state, cfg, stream_mode="values"):
        transcript.append(state["obs"])
        steps += 1

        if state.get("done"):
            done = True
            break
        if max_steps and steps >= max_steps:
            print(f"\n[Runner] Step limit {max_steps} reached; ending.")
            break

    return transcript, done


def run_single_action(engine: ZorkinatorEngine, action: str) -> None:
    obs, _ = engine.env.reset()
    print("[Env Start]", obs)
    obs, *_ = engine.env.step(action)
    print("[Env Response]", obs.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Zorkinator agent with YAML+--opts config"
    )
    parser.add_argument(
        "--config-file", "-c",
        required=True,
        help="Path to YAML config (see config.yaml)"
    )
    parser.add_argument(
        "--opts",
        nargs=argparse.REMAINDER,
        help="Override config options: KEY=VALUE ..."
    )
    parser.add_argument(
        "--action",
        help="Run one action and exit"
    )
    args = parser.parse_args()

    # 1) Load base YAML config
    cfg = OmegaConf.load(args.config_file)

    # 2) Apply CLI overrides via --opts
    if args.opts:
        override_conf = OmegaConf.from_dotlist(args.opts)
        cfg = OmegaConf.merge(cfg, override_conf)

    # 3) Instantiate shared Ollama client
    client = OllamaClient(
        model=cfg.get("ollama_model"),
        base_url=cfg.get("ollama_base_url")
    )

    # 4) Dynamically build components
    reasoner_path   = f"engine.components.reasoners.{cfg.reasoner}"
    evaluator_path  = f"engine.components.evaluators.{cfg.evaluator}"
    reflector_path  = f"engine.components.reflectors.{cfg.reflector}"

    reasoner  = instantiate_class(reasoner_path, client)
    evaluator = instantiate_class(evaluator_path, client)
    reflector = instantiate_class(reflector_path, client)

    # 5) Create the engine
    engine = ZorkinatorEngine(
        game_path=cfg.game_file,
        reasoner=reasoner,
        evaluator=evaluator,
        reflector=reflector
    )

    # 6) Single-action shortcut
    if args.action:
        run_single_action(engine, args.action)
        return

    # 7) Full episode run
    print("🚀 Zorkinator modular engine started")
    cap = cfg.get("episode_max_steps")
    transcript, done = run_episode(engine, cap)

    # 8) Post-run evaluation
    report = evaluate_run(engine.env, transcript, done=done)
    print("\n🧠 Final Evaluation Report")
    for k, v in report.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()