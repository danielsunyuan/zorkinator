#!/bin/bash
set -e

SESSION_ID="player1"

# Cleanup in case of re-run
curl -s -X POST "http://localhost:8000/end?session_id=${SESSION_ID}" > /dev/null || true

# Start new game session
echo "▶ Starting session..."
curl -sSf -X POST "http://localhost:8000/start?session_id=${SESSION_ID}" | jq

# Step 1: open mailbox
echo "▶ Step: open mailbox"
curl -sSf -X POST "http://localhost:8000/step?session_id=${SESSION_ID}" \
     -H "Content-Type: application/json" \
     -d '{"action": "open mailbox"}' | jq

# Step 2: take leaflet
echo "▶ Step: take leaflet"
curl -sSf -X POST "http://localhost:8000/step?session_id=${SESSION_ID}" \
     -H "Content-Type: application/json" \
     -d '{"action": "take leaflet"}' | jq

# Step 3: check inventory
echo "▶ Step: inventory"
curl -sSf -X POST "http://localhost:8000/step?session_id=${SESSION_ID}" \
     -H "Content-Type: application/json" \
     -d '{"action": "inventory"}' | jq

# End session
echo "▶ Ending session..."
curl -sSf -X POST "http://localhost:8000/end?session_id=${SESSION_ID}" | jq
