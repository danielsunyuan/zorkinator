import os
from typing import Dict, Tuple, Any

from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
import jericho

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_GAME = os.environ.get("GAME_FILE")
if not DEFAULT_GAME:
    raise ValueError("GAME_FILE environment variable not set (e.g. jericho/games/.../zork1.z5)")

app = FastAPI(title="Jericho Z-Machine API")

# ---------------------------------------------------------------------------
# Data Stores (in-memory, per-container)
# ---------------------------------------------------------------------------

games: Dict[str, jericho.FrotzEnv] = {}                     # session_id -> env
infos: Dict[str, Dict[str, Any]] = {}                       # session_id -> last info dict
saves: Dict[Tuple[str, str], bytes] = {}                    # (session_id, slot) -> serialized state

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Command(BaseModel):
    action: str

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def require_session(session_id: str) -> jericho.FrotzEnv:
    env = games.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return env

# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------

@app.post("/start", summary="Start a new game session")
def start_game(session_id: str = Query(...), game_file: str | None = Query(None)):
    if session_id in games:
        raise HTTPException(status_code=400, detail=f"Session '{session_id}' already exists")

    game_path = game_file or DEFAULT_GAME
    env = jericho.FrotzEnv(game_path)
    obs, info = env.reset()
    games[session_id] = env
    infos[session_id] = info
    return {"session_id": session_id, "response": obs}

@app.post("/end", summary="Delete a session and free memory")
def end_game(session_id: str):
    env = games.pop(session_id, None)
    infos.pop(session_id, None)
    if env:
        env.close()
    return {"message": f"Session '{session_id}' ended"}

# ---------------------------------------------------------------------------
# Core Gameplay
# ---------------------------------------------------------------------------

@app.post("/step", summary="Send a command and advance the game")
def step(command: Command, session_id: str = Query(...)):
    env = require_session(session_id)
    obs, reward, done, info = env.step(command.action)
    infos[session_id] = info
    return {
        "response": obs,
        "reward": reward,
        "score": env.get_score(),
        "moves": env.get_moves(),
        "done": done,
    }

@app.get("/reset", summary="Reset the game to the start state")
def reset(session_id: str = Query(...)):
    env = require_session(session_id)
    obs, info = env.reset()
    infos[session_id] = info
    return {"response": obs, "score": env.get_score(), "moves": env.get_moves()}

# ---------------------------------------------------------------------------
# State & Introspection
# ---------------------------------------------------------------------------

@app.get("/state", summary="Full snapshot of current game state")
def get_state(session_id: str = Query(...)):
    env = require_session(session_id)
    description, *_ = env.step("look")              # re-describe room (safe)
    return {
        "score": env.get_score(),
        "moves": env.get_moves(),
        "location": env.get_world_state_hash(),
        "inventory": env.get_inventory(),
        "description": description,
    }

@app.get("/valid-actions", summary="Parser-validated verb-object pairs")
def get_valid_actions(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"valid_actions": env.get_valid_actions()}

@app.get("/inventory", summary="Current inventory text")
def get_inventory(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"inventory": env.get_inventory()}

@app.get("/player-location", summary="Room object for player location")
def get_player_location(session_id: str = Query(...)):
    env = require_session(session_id)
    room = env.get_player_location()
    return {
        "name": getattr(room, "name", ""),
        "description": getattr(room, "description", ""),
        "contents": [obj.name for obj in getattr(room, "contents", []) if hasattr(obj, "name")],
    }

@app.get("/game-over", summary="Is the game over?")
def game_over(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"game_over": env.game_over()}

@app.get("/victory", summary="Did the player win?")
def victory(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"victory": env.victory()}

# ---------------------------------------------------------------------------
# Save / Load
# ---------------------------------------------------------------------------

@app.post("/save", summary="Save state to a slot (in-memory)")
def save_state(session_id: str = Query(...), slot: str = Query(...)):
    env = require_session(session_id)
    saves[(session_id, slot)] = env.get_state()
    return {"message": f"Saved session '{session_id}' to slot '{slot}'"}

@app.post("/load", summary="Load state from a slot")
def load_state(session_id: str = Query(...), slot: str = Query(...)):
    env = require_session(session_id)
    state = saves.get((session_id, slot))
    if state is None:
        raise HTTPException(status_code=404, detail="Save slot not found")
    env.set_state(state)
    return {"message": f"Loaded slot '{slot}' for session '{session_id}'"}

# ---------------------------------------------------------------------------
# Misc Utilities
# ---------------------------------------------------------------------------

@app.get("/dictionary", summary="Return game's parser dictionary")
def get_dictionary(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"dictionary": env.get_dictionary()}

@app.get("/max-score", summary="Maximum attainable score")
def get_max_score(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"max_score": env.get_max_score()}

@app.get("/supported", summary="Is the game fully supported by Jericho?")
def is_supported(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"fully_supported": env.is_fully_supported()}

# ---------------------------------------------------------------------------
# Run (only if executed directly, not when imported)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
