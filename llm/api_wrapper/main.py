import os
import httpx
from fastapi import FastAPI, Request

app = FastAPI()

# These could be moved to config file or env vars
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
TGI_URL = os.getenv("TGI_URL", "http://tgi-service:80/generate")

@app.post("/generate")
async def proxy_generate(request: Request):
    payload = await request.json()
    backend = payload.pop("backend", "tgi")  # default to tgi

    async with httpx.AsyncClient(timeout=60.0) as client:
        if backend == "ollama":
            formatted = {
                "model": payload.get("model", "llama3"),
                "prompt": payload.get("inputs", "")
            }
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=formatted)
            return {"generated_text": response.json().get("response")}

        elif backend == "tgi":
            response = await client.post(f"{TGI_URL}", json=payload)
            return response.json()

        else:
            return {"error": "Unknown backend"}
