# Jericho Z-Machine API Service 🧙‍♂️

This service exposes any Infocom‑style text adventure (`.z3`, `.z4`, `.z5`, `.z8`) over a clean, session‑aware HTTP API.
It is powered by **[Jericho](https://github.com/microsoft/jericho)** (Microsoft Research) + **FastAPI** and containerised for drop‑in use inside the broader **Zorkinator** project.

---

## 📂 Directory Layout

```text
jericho/
├─ Dockerfile           # builds the API image
├─ main.py              # FastAPI app (multi‑session)
├─ requirements.txt     # fastapi • uvicorn • jericho • spacy
└─ games/               # curated Z‑machine titles (zork1.z5, planetfall.z3 …)
```

---

## 🚀 Quick Start (dev)

```bash
# from repo root
docker compose up --build jericho

# create a session
curl -X POST "http://localhost:8000/start?session_id=alpha"
```

---

## 🔧 Environment Variables

| Var         | Default                                                            | Description                                                        |
| ----------- | ------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `GAME_FILE` | `jericho/games/z-machine-games-master/jericho-game-suite/zork1.z5` | Game loaded when a session starts (can be overridden via `/start`) |

---

## 🌐 Endpoint Reference

| Route                                                   | Verb     | Description                                        | Required Query                         |
| ------------------------------------------------------- | -------- | -------------------------------------------------- | -------------------------------------- |
| `/start`                                                | **POST** | Create a new game session                          | `session_id` (`game_file` optional)    |
| `/end`                                                  | **POST** | Destroy a session                                  | `session_id`                           |
| `/reset`                                                | **GET**  | Restart session at turn 0                          | `session_id`                           |
| `/step`                                                 | **POST** | Send a command & advance                           | `session_id`, JSON `{ "action": "…" }` |
| `/state`                                                | **GET**  | Snapshot: score, moves, hash, inventory, room text | `session_id`                           |
| `/save` / `/load`                                       | **POST** | In‑memory save slots                               | `session_id`, `slot`                   |
| `/valid-actions`                                        | **GET**  | Parser‑validated verb–object pairs                 | `session_id`                           |
| `/player-location`                                      | **GET**  | Current room & contents                            | `session_id`                           |
| `/game-over` / `/victory`                               | **GET**  | End‑of‑game / win flag                             | `session_id`                           |
| `/inventory`, `/dictionary`, `/max-score`, `/supported` | **GET**  | Misc helpers                                       | `session_id`                           |

*All responses are JSON; errors return FastAPI standard `404 / 422 / 400` codes.*

---

## 🧪 Smoke Test

```bash
SID="demo"

curl -X POST "http://localhost:8000/start?session_id=$SID"

curl -X POST "http://localhost:8000/step?session_id=$SID" \
     -H "Content-Type: application/json" -d '{"action":"open mailbox"}'

curl "http://localhost:8000/state?session_id=$SID" | jq

curl "http://localhost:8000/save?session_id=$SID&slot=chk1"
curl "http://localhost:8000/load?session_id=$SID&slot=chk1"

curl -X POST "http://localhost:8000/end?session_id=$SID"
```

---

## 🏗️ GitHub Actions CI

A workflow (`.github/workflows/jericho-ci.yml`) builds the image, launches the service, and runs the smoke‑test on every push/PR touching `jericho/`.

---

## 📝 Development Notes

* **Sessions live in RAM.** Restarting the container clears all games & saves.
* **spaCy model** `en_core_web_sm` is pre‑installed during image build.
* **Scaling:** run many containers or many sessions in one container—both patterns work.
* **Interactive docs:** Swagger UI available at [`/docs`](http://localhost:8000/docs).

Happy adventuring! 🔑
