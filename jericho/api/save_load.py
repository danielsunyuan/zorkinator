from fastapi import APIRouter, HTTPException, Query
from .utils import require_session, saves

router = APIRouter()

@router.post("/save", summary="Save state to slot")
def save_state(session_id: str = Query(...), slot: str = Query(...)):
    env = require_session(session_id)
    saves[(session_id, slot)] = env.get_state()
    return {"message": f"Saved '{session_id}' to slot '{slot}'"}

@router.post("/load", summary="Load state from slot")
def load_state(session_id: str = Query(...), slot: str = Query(...)):
    env = require_session(session_id)
    state = saves.get((session_id, slot))
    if not state:
        raise HTTPException(status_code=404, detail="Slot not found")
    env.set_state(state)
    return {"message": f"Loaded slot '{slot}' for '{session_id}'"}