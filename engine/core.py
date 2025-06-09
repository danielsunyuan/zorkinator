import os
import sys
import threading
from typing import Protocol, List
from jericho import FrotzEnv
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig

# ──────────────────────────────────────────────────────────────────────
# 1. AgentState definition (used in LangGraph)
# ──────────────────────────────────────────────────────────────────────
class AgentState(dict):
    obs: str
    memory: str
    last_action: str
    seen: List[str]
    reward: int
    reflection: str
    done: bool

# ──────────────────────────────────────────────────────────────────────
# 2. Protocols (Interfaces for plug-and-play components)
# ──────────────────────────────────────────────────────────────────────
class Planner(Protocol):
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str: ...

class Evaluator(Protocol):
    def evaluate(self, transcript: List[str]) -> int: ...

class Reflector(Protocol):
    def reflect(self, transcript: List[str], reward: int) -> str: ...

# ──────────────────────────────────────────────────────────────────────
# 3. Node implementations
# ──────────────────────────────────────────────────────────────────────

def think(state: AgentState, env: FrotzEnv, planner: Planner) -> AgentState:
    """
    Think node: pick an action via the Planner.
    """
    state["last_action"] = planner.choose_action(state, env)
    return state


def act(state: AgentState, env: FrotzEnv) -> AgentState:
    """
    Act node: execute last_action, update obs, memory, seen, and done flag.
    """
    obs, _, _, done = env.step(state["last_action"])
    obs = obs.strip()
    print(f"> {state['last_action']}\n{obs}\n")
    state["memory"] += f"\n> {state['last_action']}\n{obs}"
    state["seen"].append(f"{obs}::{state['last_action']}")
    state["obs"] = obs
    state["done"] = done
    return state


def evaluate(state: AgentState, evaluator: Evaluator) -> AgentState:
    """
    Evaluate node: compute reward based on memory transcript.
    """
    transcript = state["memory"].splitlines()
    state["reward"] = evaluator.evaluate(transcript)
    return state


def reflect(state: AgentState, reflector: Reflector) -> AgentState:
    """
    Reflect node: generate reflection based on transcript + reward, append to memory.
    """
    transcript = state["memory"].splitlines()
    reflection = reflector.reflect(transcript, state["reward"])
    state["reflection"] = reflection
    state["memory"] += f"\n[Reflection]\n{reflection}"
    return state

# ──────────────────────────────────────────────────────────────────────
# 4. Engine orchestration
# ──────────────────────────────────────────────────────────────────────
class ZorkinatorEngine:
    def __init__(
        self,
        game_path: str,
        planner: Planner,
        evaluator: Evaluator,
        reflector: Reflector
    ):
        self.env = FrotzEnv(game_path)
        obs0, _ = self.env.reset()
        self.planner = planner
        self.evaluator = evaluator
        self.reflector = reflector

        builder = StateGraph(AgentState)
        builder.add_node("think",    lambda s: think(s, self.env, self.planner))
        builder.add_node("act",      lambda s: act(s, self.env))
        builder.add_node("evaluate", lambda s: evaluate(s, self.evaluator))
        builder.add_node("reflect",  lambda s: reflect(s, self.reflector))

        builder.set_entry_point("think")
        builder.add_edge("think",    "act")
        builder.add_edge("act",      "evaluate")
        builder.add_edge("evaluate", "reflect")
        builder.add_edge("reflect",  "think")
        self.graph = builder.compile()

        # initialize full state
        self.initial_state = AgentState(
            obs=obs0,
            memory="",
            last_action="",
            seen=[],
            reward=0,
            reflection="",
            done=False
        )

        # handle Ctrl-D
        threading.Thread(target=self._watch_eof, daemon=True).start()

    def _watch_eof(self):
        for _ in sys.stdin: pass
        print("\n[Engine] EOF detected — exiting.")
        os._exit(0)

    def run(self):
        print("🚀 Zorkinator modular engine started")
        cfg = RunnableConfig(recursion_limit=1_000_000)
        for step, (node, state) in enumerate(
            self.graph.stream(self.initial_state, cfg, stream_mode="updates"),
            start=1
        ):
            print(f"[Step {step}] Node={node}, Action={state['last_action']}, Reward={state['reward']}")
            if state.get("done"):
                print("[Engine] Terminal state reached. Exiting loop.")
                break