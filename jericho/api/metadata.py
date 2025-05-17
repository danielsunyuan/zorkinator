from fastapi import APIRouter, HTTPException, Query
from .utils import require_session

router = APIRouter()

@router.get("/inventory", summary="Inventory list")
def get_inventory(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"inventory": env.get_inventory()}

@router.get("/player-location", summary="Room details")
def get_player_location(session_id: str = Query(...)):
    env = require_session(session_id)
    room = env.get_player_location()
    return {"name": getattr(room, "name", ""), "description": getattr(room, "description", ""), "contents": [obj.name for obj in getattr(room, "contents", []) if hasattr(obj, "name")]}

@router.get("/game-over", summary="Game over flag")
def game_over(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"game_over": env.game_over()}

@router.get("/victory", summary="Victory flag")
def victory(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"victory": env.victory()}

@router.get("/dictionary", summary="Parser dictionary")
def get_dictionary(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"dictionary": env.get_dictionary()}

@router.get("/max-score", summary="Max attainable score")
def get_max_score(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"max_score": env.get_max_score()}

@router.get("/supported", summary="Full support check")
def is_supported(session_id: str = Query(...)):
    env = require_session(session_id)
    return {"fully_supported": env.is_fully_supported()}

@router.get("/walkthrough", summary="Golden path walkthrough")
def get_walkthrough(session_id: str = Query(...)):
    env = require_session(session_id)
    try:
        walkthrough = env.get_walkthrough()
        if not walkthrough:
            raise ValueError
        return {"walkthrough": walkthrough}
    except Exception:
        raise HTTPException(status_code=404, detail="Walkthrough unavailable")