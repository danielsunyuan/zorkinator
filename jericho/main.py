import os
import jericho
from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

game_file = os.environ.get("GAME_FILE")
if not game_file:
    raise ValueError("GAME_FILE environment variable not set.")

env = jericho.FrotzEnv('/app/games/zork1.z5')
obs, info = env.reset()

class Command(BaseModel):
    action: str

@app.get("/reset")
def reset():
    global obs, info
    obs, info = env.reset()
    return {"response": obs, "score": info["score"], "moves": info["moves"]}

@app.post("/step")
def step(command: Command):
    global obs, info
    obs, reward, done, info = env.step(command.action)
    return {
        "response": obs,
        "reward": reward,
        "score": info["score"],
        "moves": info["moves"],
        "done": done
    }