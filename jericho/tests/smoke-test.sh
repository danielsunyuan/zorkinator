#!/bin/bash
set -e

SID="ci-test"

curl -sSf -X POST "http://localhost:8000/start?session_id=$SID"
curl -sSf "http://localhost:8000/state?session_id=$SID"
curl -sSf -X POST "http://localhost:8000/step?session_id=$SID" \
     -H "Content-Type: application/json" \
     -d '{"action": "open mailbox"}'
curl -sSf -X POST "http://localhost:8000/save?session_id=$SID&slot=ci"
curl -sSf -X POST "http://localhost:8000/load?session_id=$SID&slot=ci"
curl -sSf "http://localhost:8000/game-over?session_id=$SID"
curl -sSf "http://localhost:8000/valid-actions?session_id=$SID"
curl -sSf "http://localhost:8000/walkthrough?session_id=$SID"
curl -sSf -X POST "http://localhost:8000/end?session_id=$SID"
