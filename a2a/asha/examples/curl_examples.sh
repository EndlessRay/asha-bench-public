#!/bin/bash
# Asha A2A — curl Examples
# Replace YOUR_API_KEY with your actual key

API_KEY="${ASHA_API_KEY:-YOUR_API_KEY}"
BASE="https://api.askasha.org"

echo "=== 1. Discover Agent Card ==="
curl -s "$BASE/.well-known/agent-card.json?agent_id=asha" | python3 -m json.tool

echo ""
echo "=== 2. Medical Q&A ==="
curl -s -X POST "$BASE/a2a/v1/message:send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role": "user", "parts": [{"text": "What is the mechanism of action of metformin?"}]},
    "metadata": {"agent_id": "asha"}
  }' | python3 -m json.tool

echo ""
echo "=== 3. Drug Interaction Check ==="
curl -s -X POST "$BASE/a2a/v1/message:send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role": "user", "parts": [{"text": "Check interactions between warfarin, amiodarone, and omeprazole"}]},
    "metadata": {"agent_id": "asha"}
  }' | python3 -m json.tool

echo ""
echo "=== 4. List Recent Tasks ==="
curl -s "$BASE/a2a/v1/tasks?limit=5" \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool
