import os
from typing import Dict, Any, Tuple
from fastapi import HTTPException
import jericho

# In-memory stores

games: Dict[str, jericho.FrotzEnv] = {}
infos: Dict[str, Dict[str, Any]] = {}
saves: Dict[Tuple[str, str], bytes] = {}

# Default game path from env
DEFAULT_GAME = os.environ.get("GAME_FILE")
if not DEFAULT_GAME:
    raise RuntimeError("GAME_FILE not set in environment")

# Helper to ensure session exists

def require_session(session_id: str) -> jericho.FrotzEnv:
    env = games.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return env