"""
Asha A2A Client — Python Example
=================================
Query Asha's medical AI via the A2A protocol.

Usage:
    # Get a free API key first:
    # curl -X POST https://api.askasha.org/api/a2a/signup \
    #   -H "Content-Type: application/json" \
    #   -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

    ASHA_API_KEY=your_key python python_client.py
"""

import json
import os
import sys

import requests

BASE_URL = "https://api.askasha.org"
API_KEY = os.getenv("ASHA_API_KEY", "")


def discover():
    """Fetch the agent card to discover capabilities."""
    r = requests.get(f"{BASE_URL}/.well-known/agent-card.json", params={"agent_id": "asha"})
    r.raise_for_status()
    card = r.json()
    print(f"Agent: {card['name']} v{card['version']}")
    print(f"Provider: {card['provider']['organization']}")
    for skill in card["skills"]:
        print(f"  [{skill['id']}] {skill['name']}")
    if "epistemicCapabilities" in card:
        ec = card["epistemicCapabilities"]
        corpus = ec.get("knowledgeCorpus", {})
        print(f"  Knowledge: {corpus.get('totalVectors', '?')} vectors across {len(corpus.get('collections', []))} collections")
        print(f"  Falsification: {ec.get('falsificationAvailable', False)}")
        print(f"  Provenance: {ec.get('provenanceInResponses', False)}")
    return card


def query(text: str, agent_id: str = "asha") -> dict:
    """Send a question and return the completed task."""
    r = requests.post(
        f"{BASE_URL}/a2a/v1/message:send",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "message": {"role": "user", "parts": [{"text": text}]},
            "metadata": {"agent_id": agent_id},
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["task"]


def parse(task: dict) -> tuple:
    """Extract response text and provenance from task artifacts."""
    response_text = ""
    provenance = {}
    for artifact in task.get("artifacts", []):
        if artifact.get("name") == "response" and artifact.get("parts"):
            response_text = artifact["parts"][0].get("text", "")
        elif artifact.get("name") == "provenance" and artifact.get("parts"):
            provenance = artifact["parts"][0].get("data", {})
    return response_text, provenance


def check_usage() -> dict:
    """Check remaining quota for your API key."""
    r = requests.get(
        f"{BASE_URL}/api/a2a/usage",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def main():
    if not API_KEY:
        print("Set ASHA_API_KEY environment variable.")
        print("Get a free key: curl -X POST https://api.askasha.org/api/a2a/signup \\")
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"email":"you@example.com","name":"Your Name","tier":"free"}\'')
        sys.exit(1)

    print("=" * 60)
    print("Asha A2A Client")
    print("=" * 60)

    discover()

    print("\n--- Usage ---")
    usage = check_usage()
    print(f"Tier: {usage.get('tier', '?')}")
    print(f"Today: {usage.get('queries_today', '?')}/{usage.get('daily_limit', '?')}")
    print(f"Month: {usage.get('queries_this_month', '?')}/{usage.get('monthly_limit', '?')}")

    queries = [
        "What are the interactions between warfarin and amiodarone?",
        "What are the USPSTF screening recommendations for colorectal cancer?",
    ]

    for i, q in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {q}")
        task = query(q)
        text, prov = parse(task)

        print(f"State: {task['status']['state']}")
        print(f"Sources: {prov.get('sources', [])}")
        print(f"Evidence: {prov.get('evidence_count', 0)} items")
        print(f"Scope: {prov.get('predicate_scope', [])}")
        print(f"Answer: {text[:300]}...")


if __name__ == "__main__":
    main()
