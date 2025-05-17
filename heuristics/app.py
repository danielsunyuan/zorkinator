from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

class HeuristicRequest(BaseModel):
    observation: str
    inventory: list[str] = []
    actions_history: list[str] = []

@app.post("/heuristics")
def compute_heuristics(payload: HeuristicRequest) -> Dict:
    obs = payload.observation.lower()

    # Minimal logic — this is where you'd grow complexity
    if "narrow" in obs or "tight" in obs:
        mode = "claustrophobic_mode"
        temp = 1.2
    elif "light" in obs or "exit" in obs:
        mode = "hopeful_mode"
        temp = 0.8
    else:
        mode = "default"
        temp = 1.0

    return {
        "adapter": mode,
        "decoding_params": {
            "temperature": temp
        }
    }
