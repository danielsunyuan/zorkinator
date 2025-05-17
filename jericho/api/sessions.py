from fastapi import APIRouter, HTTPException, Query
import jericho
from .utils import games, infos, DEFAULT_GAME

router = APIRouter()

@router.post("/start", summary="Start new session")
def start_game(session_id: str = Query(...), game_file: str | None = Query(None)):
    if session_id in games:
        raise HTTPException(status_code=400, detail="Session already exists")
    path = game_file or DEFAULT_GAME
    env = jericho.FrotzEnv(path)
    obs, info = env.reset()
    games[session_id] = env
    infos[session_id] = info
    return {"session_id": session_id, "response": obs}

@router.post("/end", summary="End session")
def end_game(session_id: str = Query(...)):
    env = games.pop(session_id, None)
    infos.pop(session_id, None)
    if env:
        env.close()
    return {"message": f"Session '{session_id}' ended"}