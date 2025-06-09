# run.py
import argparse
import json
from typing import List

from engine.engine_core import ZorkinatorEngine
from evaluator.post_run import evaluate_run
from utils.config_loader import build_components
from utils.difficulty_profiles import apply_difficulty
from langchain_core.runnables import RunnableConfig


def run_episode(engine: ZorkinatorEngine, max_steps: int | None) -> List[str]:
    """Stream LangGraph, collect transcript, obey optional step cap."""
    transcript = [engine.initial_state["obs"]]
    cfg = RunnableConfig(recursion_limit=1_000_000)
    graph_state = engine.initial_state
    steps, done = 0, False

    for graph_state in engine.graph.stream(graph_state, cfg, stream_mode="values"):
        steps += 1
        transcript.append(graph_state["obs"])

        if graph_state.get("done"):
            done = True
            break
        if max_steps and steps >= max_steps:
            print(f"\n[Runner] Step limit of {max_steps} reached. Ending run.")
            break

    return transcript, done


def run_single_action(engine: ZorkinatorEngine, action: str) -> None:
    """Execute a single action, show the response, then exit."""
    env = engine.env
    obs, _ = env.reset()
    print("[Env Start]", obs)
    obs, *_ = env.step(action)
    print("[Env Response]", obs.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Zorkinator agent.")
    parser.add_argument("--config", default="config.json",
                        help="Path to config file")
    parser.add_argument("--action", help="Run one action and exit")
    parser.add_argument("--max-steps", type=int,
                        help="Optional step limit (overrides profile)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard", "rogue"],
                        help="Override difficulty in config/profile")
    args = parser.parse_args()

    # ── Load + apply difficulty profile
    with open(args.config) as f:
        config = json.load(f)
    if args.difficulty:
        config["difficulty"] = args.difficulty
    config = apply_difficulty(config)        # fills in planner, loop, etc.

    # ── Build components & engine
    planner, loop = build_components(config)
    engine = ZorkinatorEngine(config["game_file"], planner, loop)

    # ── Single-action shortcut
    if args.action:
        run_single_action(engine, args.action)
        return

    # ── Episode run
    print("🚀 Zorkinator modular engine started")
    cap = args.max_steps or config.get("episode_max_steps")
    transcript, done = run_episode(engine, cap)

    # ── Post-run evaluation
    report = evaluate_run(engine.env, transcript, done=done)
    print("\n🧠 Final Evaluation Report")
    for k, v in report.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()