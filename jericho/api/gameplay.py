from fastapi import APIRouter, Query
from pydantic import BaseModel
from .utils import require_session, infos

router = APIRouter()

class Command(BaseModel):
    action: str

@router.post("/step", summary="Advance one turn")
def step(command: Command, session_id: str = Query(...)):
    env = require_session(session_id)
    obs, reward, done, info = env.step(command.action)
    infos[session_id] = info
    return {"response": obs, "reward": reward, "score": env.get_score(), "moves": env.get_moves(), "done": done}

@router.get("/reset", summary="Reset game")
def reset(session_id: str = Query(...)):
    env = require_session(session_id)
    obs, info = env.reset()
    infos[session_id] = info
    return {"response": obs, "score": env.get_score(), "moves": env.get_moves()}

@router.get("/state", summary="Current state snapshot")
def get_state(session_id: str = Query(...)):
    env = require_session(session_id)
    description, *_ = env.step("look")
    return {"score": env.get_score(), "moves": env.get_moves(), "location": env.get_world_state_hash(), "inventory": env.get_inventory(), "description": description}

@router.get("/valid-actions", summary="Parser-backed actions")
def get_valid_actions(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"valid_actions": env.get_valid_actions()}