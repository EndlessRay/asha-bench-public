#!/bin/bash
# Asha A2A — curl Examples
# Get a free API key first:
#   curl -X POST https://api.askasha.org/api/a2a/signup \
#     -H "Content-Type: application/json" \
#     -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

API_KEY="${ASHA_API_KEY:-YOUR_API_KEY}"
BASE="https://api.askasha.org"

echo "=== 1. Discover Agent ==="
curl -s "$BASE/.well-known/agent-card.json?agent_id=asha" | python3 -m json.tool

echo ""
echo "=== 2. Check Health ==="
curl -s "$BASE/a2a/v1/health" | python3 -m json.tool

echo ""
echo "=== 3. Medical Q&A ==="
curl -s -X POST "$BASE/a2a/v1/message:send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role": "user", "parts": [{"text": "What is the mechanism of action of metformin?"}]},
    "metadata": {"agent_id": "asha"}
  }' | python3 -m json.tool

echo ""
echo "=== 4. Drug Interaction Check ==="
curl -s -X POST "$BASE/a2a/v1/message:send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {"role": "user", "parts": [{"text": "Check interactions between warfarin, amiodarone, and omeprazole"}]},
    "metadata": {"agent_id": "asha"}
  }' | python3 -m json.tool

echo ""
echo "=== 5. Check Usage ==="
curl -s "$BASE/api/a2a/usage" \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool

echo ""
echo "=== 6. List Recent Tasks ==="
curl -s "$BASE/a2a/v1/tasks?limit=5" \
  -H "Authorization: Bearer $API_KEY" | python3 -m json.tool
