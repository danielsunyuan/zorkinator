# engine_core.py

from typing import Protocol, List, Tuple
from jericho import FrotzEnv
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig
import threading
import random
import sys

# ──────────────────────────────────────────────────────────────────────
# 1. AgentState definition (used in LangGraph)
# ──────────────────────────────────────────────────────────────────────
class AgentState(dict):
    obs: str
    memory: str
    last_action: str
    seen: List[str]

# ──────────────────────────────────────────────────────────────────────
# 2. Protocols (Interfaces for plug-and-play components)
# ──────────────────────────────────────────────────────────────────────
class Planner(Protocol):
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str: ...

class LoopHeuristic(Protocol):
    def avoid_loop(self, state: AgentState, action: str) -> str: ...

class Evaluator(Protocol):
    def evaluate(self, transcript: List[str]) -> int: ...

class Reflector(Protocol):
    def reflect(self, transcript: List[str], reward: int) -> str: ...

# ──────────────────────────────────────────────────────────────────────
# 3. Concrete Implementations (basic stubs for now)
# ──────────────────────────────────────────────────────────────────────
class RandomPlanner:
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str:
        return random.choice(["look", "north", "south", "east", "west"])

class NoLoopHeuristic:
    def avoid_loop(self, state: AgentState, action: str) -> str:
        return action

class NullEvaluator:
    def evaluate(self, transcript: List[str]) -> int:
        return 0

class NullReflector:
    def reflect(self, transcript: List[str], reward: int) -> str:
        return ""

# ──────────────────────────────────────────────────────────────────────
# 4. Think / Act node logic
# ──────────────────────────────────────────────────────────────────────
def think(state: AgentState, env: FrotzEnv, planner: Planner, loop: LoopHeuristic) -> AgentState:
    action = planner.choose_action(state, env)
    action = loop.avoid_loop(state, action)
    state["last_action"] = action
    return state

def act(state: AgentState, env: FrotzEnv) -> AgentState:
    obs, _, _, _ = env.step(state["last_action"])
    obs = obs.strip()
    print(f"> {state['last_action']}\n{obs}\n")
    state["memory"] += f"\n> {state['last_action']}\n{obs}"
    state["seen"].append(f"{obs}::{state['last_action']}")
    state["obs"] = obs
    return state

# ──────────────────────────────────────────────────────────────────────
# 5. Engine
# ──────────────────────────────────────────────────────────────────────
class ZorkinatorEngine:
    def __init__(self, game_path: str, planner: Planner, loop: LoopHeuristic):
        self.env = FrotzEnv(game_path)
        obs0, _ = self.env.reset()
        self.planner = planner
        self.loop = loop

        builder = StateGraph(AgentState)
        builder.add_node("think", lambda s: think(s, self.env, self.planner, self.loop))
        builder.add_node("act", lambda s: act(s, self.env))
        builder.set_entry_point("think")
        builder.add_edge("think", "act")
        builder.add_edge("act", "think")
        self.graph = builder.compile()

        self.initial_state = AgentState(obs=obs0, memory="", last_action="", seen=[])

        threading.Thread(target=self._watch_eof, daemon=True).start()

    def _watch_eof(self):
        for _ in sys.stdin:
            pass
        print("\n[Engine] EOF detected — exiting.")
        os._exit(0)

    def run(self):
        print("🚀 Zorkinator modular engine started")
        cfg = RunnableConfig(recursion_limit=1_000_000)
        for _ in self.graph.stream(self.initial_state, cfg):
            pass