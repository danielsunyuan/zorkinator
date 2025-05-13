#!/bin/bash
set -e

# Cleanup (in case script is rerun)
curl -s -X POST "http://localhost:8000/end?session_id=player1" > /dev/null || true
curl -s -X POST "http://localhost:8000/end?session_id=player2" > /dev/null || true

# Start sessions
echo "▶ Starting session for player1..."
curl -sSf -X POST "http://localhost:8000/start?session_id=player1" | jq

echo "▶ Starting session for player2..."
curl -sSf -X POST "http://localhost:8000/start?session_id=player2" | jq

# Step session player1
echo "▶ player1: open mailbox"
curl -sSf -X POST "http://localhost:8000/step?session_id=player1" \
    -H "Content-Type: application/json" \
    -d '{"action": "open mailbox"}' | jq

# Step session player2
echo "▶ player2: look"
curl -sSf -X POST "http://localhost:8000/step?session_id=player2" \
    -H "Content-Type: application/json" \
    -d '{"action": "look"}' | jq

# End sessions
echo "▶ Ending session for player1..."
curl -sSf -X POST "http://localhost:8000/end?session_id=player1" | jq

echo "▶ Ending session for player2..."
curl -sSf -X POST "http://localhost:8000/end?session_id=player2" | jq
