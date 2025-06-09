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
class Reasoner(Protocol):
    """
    Provides the next action based on the current state and environment.
    """
    def choose_action(self, state: AgentState, env: FrotzEnv) -> str: ...

class Evaluator(Protocol):
    """
    Computes a scalar reward from the transcript of past turns.
    """
    def evaluate(self, transcript: List[str]) -> int: ...

class Reflector(Protocol):
    """
    Generates a reflection string given the transcript and reward.
    """
    def reflect(self, transcript: List[str], reward: int) -> str: ...

# ──────────────────────────────────────────────────────────────────────
# 3. Node implementations (Reason, Act, Observe, Reflect)
# ──────────────────────────────────────────────────────────────────────

def reason(state: AgentState, env: FrotzEnv, reasoner: Reasoner) -> AgentState:
    """
    Reason node: choose the next action via the Reasoner.
    """
    state["last_action"] = reasoner.choose_action(state, env)
    return state


def act(state: AgentState, env: FrotzEnv) -> AgentState:
    """
    Act node: execute the last action in the env, update obs/memory/seen,
    and set the done flag.
    """
    action = state["last_action"]
    obs, _, done, _ = env.step(action)
    obs = obs.strip()
    print(f"> {action}\n{obs}\n")
    state["obs"] = obs
    state["memory"] += f"\n> {action}\n{obs}"
    state["seen"].append(f"{obs}::{action}")
    state["done"] = done
    return state


def observe(state: AgentState, evaluator: Evaluator) -> AgentState:
    """
    Observe node: compute reward based on memory transcript.
    """
    transcript = state["memory"].splitlines()
    state["reward"] = evaluator.evaluate(transcript)
    return state


def reflect_node(state: AgentState, reflector: Reflector) -> AgentState:
    """
    Reflect node: generate and append a reflection based on transcript and reward.
    """
    transcript = state["memory"].splitlines()
    reflection = reflector.reflect(transcript, state["reward"])
    state["reflection"] = reflection
    state["memory"] += f"\n[Reflection]\n{reflection}"
    return state

# ──────────────────────────────────────────────────────────────────────
# 4. Engine orchestration with LangGraph
# ──────────────────────────────────────────────────────────────────────
class ZorkinatorEngine:
    def __init__(
        self,
        game_path: str,
        reasoner: Reasoner,
        evaluator: Evaluator,
        reflector: Reflector
    ):
        self.env = FrotzEnv(game_path)
        obs0, _ = self.env.reset()
        self.reasoner = reasoner
        self.evaluator = evaluator
        self.reflector = reflector

        builder = StateGraph(AgentState)
        builder.add_node("reason",  lambda s: reason(s, self.env, self.reasoner))
        builder.add_node("act",     lambda s: act(s, self.env))
        builder.add_node("observe", lambda s: observe(s, self.evaluator))
        builder.add_node("reflect", lambda s: reflect_node(s, self.reflector))

        builder.set_entry_point("reason")
        builder.add_edge("reason",  "act")
        builder.add_edge("act",     "observe")
        builder.add_edge("observe", "reflect")
        builder.add_edge("reflect", "reason")
        self.graph = builder.compile()

        self.initial_state = AgentState(
            obs=obs0,
            memory="",
            last_action="",
            seen=[],
            reward=0,
            reflection="",
            done=False
        )

        threading.Thread(target=self._watch_eof, daemon=True).start()

    def _watch_eof(self):
        for _ in sys.stdin: pass
        print("\n[Engine] EOF detected — exiting.")
        os._exit(0)

    def run(self):
        print("🚀 Zorkinator modular engine started")
        cfg = RunnableConfig(recursion_limit=1_000_000)
        for step, (phase, state) in enumerate(
            self.graph.stream(self.initial_state, cfg, stream_mode="updates"),
            start=1
        ):
            print(f"[Step {step}] Phase={phase}, Action={state['last_action']}, Reward={state['reward']}")
            if state.get("done"):
                print("[Engine] Terminal state reached. Exiting loop.")
                break