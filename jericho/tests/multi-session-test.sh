#!/bin/bash
set -e

# Use Docker hostname internally, fallback to localhost for local testing
HOST="${JERICHO_API:-http://localhost:8000}"

# Cleanup (in case script is rerun)
echo "▶ Cleaning up old sessions..."
curl -s -X POST "$HOST/end?session_id=player1" > /dev/null || true
curl -s -X POST "$HOST/end?session_id=player2" > /dev/null || true

# Start sessions
echo "▶ Starting session for player1..."
curl -sSf -X POST "$HOST/start?session_id=player1" | jq

echo "▶ Starting session for player2..."
curl -sSf -X POST "$HOST/start?session_id=player2" | jq

# Step session player1
echo "▶ player1: open mailbox"
curl -sSf -X POST "$HOST/step?session_id=player1" \
    -H "Content-Type: application/json" \
    -d '{"action": "open mailbox"}' | jq

# Step session player2
echo "▶ player2: look"
curl -sSf -X POST "$HOST/step?session_id=player2" \
    -H "Content-Type: application/json" \
    -d '{"action": "look"}' | jq

# End sessions
echo "▶ Ending session for player1..."
curl -sSf -X POST "$HOST/end?session_id=player1" | jq

echo "▶ Ending session for player2..."
curl -sSf -X POST "$HOST/end?session_id=player2" | jq
