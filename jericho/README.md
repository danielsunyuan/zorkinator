# Jericho Z-Machine API Service 🧙‍♂️

This service exposes any Infocom‑style text adventure (`.z3`, `.z4`, `.z5`, `.z8`) over a clean, session‑aware HTTP API.
It is powered by **[Jericho](https://github.com/microsoft/jericho)** (Microsoft Research) + **FastAPI** and containerised for drop‑in use inside the broader **Zorkinator** project.

## 📚 About Jericho

[Jericho](https://github.com/microsoft/jericho) is a Python interface to text-based adventure games developed by Microsoft Research. It provides a framework for reinforcement learning research on text-based games, offering:

- Parsing and interacting with Z-Machine games
- Extracting game state information and progress tracking
- Tools for machine learning agents to navigate text adventures
- Support for classic Infocom titles and modern Z-machine games

This API wraps Jericho's functionality to make it accessible via HTTP endpoints, enabling programmatic interaction with text adventure games for applications, bots, or research.

## 📂 Directory Layout

```text
jericho/
├─ Dockerfile           # builds the API image
├─ main.py              # FastAPI app (multi‑session)
├─ requirements.txt     # fastapi • uvicorn • jericho • spacy
└─ games/               # curated Z‑machine titles (zork1.z5, planetfall.z3 …)
```

## 🚀 Quick Start (dev)

```bash
# from repo root
docker compose up --build jericho

# create a session
curl -X POST "http://localhost:8000/start?session_id=alpha"
```

## 🔧 Environment Variables

| Var         | Default                                                            | Description                                                        |
| ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `GAME_FILE` | `jericho/games/z-machine-games-master/jericho-game-suite/zork1.z5` | Game loaded when a session starts (can be overridden via `/start`) |

## 🌐 API Endpoints Reference

### Session Management

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/start` | POST | Start a new game session | `session_id` (required): Unique identifier for the session<br>`game_file` (optional): Path to Z-Machine game file | `{"session_id": string, "response": string}` |
| `/end` | POST | End a game session | `session_id` (required): Session identifier | `{"message": string}` |

### Gameplay

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/step` | POST | Execute a command and advance one turn | `session_id` (required): Session identifier<br>Request body: `{"action": string}` | `{"response": string, "reward": float, "score": int, "moves": int, "done": boolean}` |
| `/reset` | GET | Reset the current game | `session_id` (required): Session identifier | `{"response": string, "score": int, "moves": int}` |
| `/state` | GET | Get a snapshot of the current game state | `session_id` (required): Session identifier | `{"score": int, "moves": int, "location": string, "inventory": array, "description": string}` |
| `/valid-actions` | GET | Get a list of valid actions at current state | `session_id` (required): Session identifier | `{"valid_actions": array}` |

### Save/Load

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/save` | POST | Save game state to a slot | `session_id` (required): Session identifier<br>`slot` (required): Save slot name | `{"message": string}` |
| `/load` | POST | Load game state from a slot | `session_id` (required): Session identifier<br>`slot` (required): Save slot name | `{"message": string}` |

### Metadata

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/inventory` | GET | Get player's inventory | `session_id` (required): Session identifier | `{"inventory": array}` |
| `/player-location` | GET | Get details about current room | `session_id` (required): Session identifier | `{"name": string, "description": string, "contents": array}` |
| `/game-over` | GET | Check if game is over | `session_id` (required): Session identifier | `{"game_over": boolean}` |
| `/victory` | GET | Check if victory condition met | `session_id` (required): Session identifier | `{"victory": boolean}` |
| `/dictionary` | GET | Get parser dictionary | `session_id` (required): Session identifier | `{"dictionary": array}` |
| `/max-score` | GET | Get maximum possible score | `session_id` (required): Session identifier | `{"max_score": int}` |
| `/supported` | GET | Check if game is fully supported | `session_id` (required): Session identifier | `{"fully_supported": boolean}` |
| `/walkthrough` | GET | Get golden path walkthrough if available | `session_id` (required): Session identifier | `{"walkthrough": array}` |

## 🧪 Example Usage

```bash
SID="demo"

# Start a new game session
curl -X POST "http://localhost:8000/start?session_id=$SID"

# Send a command
curl -X POST "http://localhost:8000/step?session_id=$SID" \
     -H "Content-Type: application/json" -d '{"action":"open mailbox"}'

# Get current state
curl "http://localhost:8000/state?session_id=$SID" | jq

# Save and load game state
curl "http://localhost:8000/save?session_id=$SID&slot=chk1"
curl "http://localhost:8000/load?session_id=$SID&slot=chk1"

# End the session
curl -X POST "http://localhost:8000/end?session_id=$SID"
```

## 🏗️ GitHub Actions CI

A workflow (`.github/workflows/jericho-ci.yml`) builds the image, launches the service, and runs the smoke‑test on every push/PR touching `jericho/`.

## 📝 Development Notes

* **Sessions live in RAM.** Restarting the container clears all games & saves.
* **spaCy model** `en_core_web_sm` is pre‑installed during image build.
* **Scaling:** run many containers or many sessions in one container—both patterns work.
* **Interactive docs:** Swagger UI available at [`/docs`](http://localhost:8000/docs).

Happy adventuring! 🔑