#!/bin/bash
set -e

# Use Docker hostname inside containers, or override from CLI
HOST="${JERICHO_API:-http://localhost:8000}"
SID="ci-test"

echo "▶ Cleaning up previous session if exists..."
curl -s -X POST "$HOST/end?session_id=$SID" > /dev/null || true

echo "▶ Starting session: $SID"
curl -sSf -X POST "$HOST/start?session_id=$SID" | jq

echo "▶ Checking state..."
curl -sSf "$HOST/state?session_id=$SID" | jq

echo "▶ Step: open mailbox"
curl -sSf -X POST "$HOST/step?session_id=$SID" \
     -H "Content-Type: application/json" \
     -d '{"action": "open mailbox"}' | jq

echo "▶ Saving game to slot: ci"
curl -sSf -X POST "$HOST/save?session_id=$SID&slot=ci" | jq

echo "▶ Loading game from slot: ci"
curl -sSf -X POST "$HOST/load?session_id=$SID&slot=ci" | jq

echo "▶ Checking if game is over..."
curl -sSf "$HOST/game-over?session_id=$SID" | jq

echo "▶ Getting valid actions..."
curl -sSf "$HOST/valid-actions?session_id=$SID" | jq

echo "▶ Fetching walkthrough..."
curl -sSf "$HOST/walkthrough?session_id=$SID" | jq

echo "▶ Ending session: $SID"
curl -sSf -X POST "$HOST/end?session_id=$SID" | jq
