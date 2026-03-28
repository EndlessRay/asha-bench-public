"""
Asha A2A Client — Python Example
=================================
Demonstrates how to query Asha's medical AI via the A2A protocol.

Usage:
    ASHA_API_KEY=your_key python python_client.py
"""

import json
import os
import sys

import requests

BASE_URL = "https://api.askasha.org"
API_KEY = os.getenv("ASHA_API_KEY", "")

def discover_agent():
    """Fetch the agent card to discover capabilities."""
    r = requests.get(f"{BASE_URL}/.well-known/agent-card.json", params={"agent_id": "asha"})
    r.raise_for_status()
    card = r.json()
    print(f"Agent: {card['name']}")
    print(f"Version: {card['version']}")
    print(f"Skills:")
    for skill in card["skills"]:
        print(f"  - {skill['name']}: {skill['description'][:80]}...")
    return card


def send_query(query: str) -> dict:
    """Send a medical question via A2A and return the task."""
    r = requests.post(
        f"{BASE_URL}/a2a/v1/message:send",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "message": {"role": "user", "parts": [{"text": query}]},
            "metadata": {"agent_id": "asha"},
        },
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["task"]


def get_task(task_id: str) -> dict:
    """Retrieve a previously completed task."""
    r = requests.get(
        f"{BASE_URL}/a2a/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["task"]


def parse_response(task: dict) -> tuple:
    """Extract response text and provenance from task artifacts."""
    response_text = ""
    provenance = {}
    for artifact in task.get("artifacts", []):
        if artifact["name"] == "response":
            response_text = artifact["parts"][0].get("text", "")
        elif artifact["name"] == "provenance":
            provenance = artifact["parts"][0].get("data", {})
    return response_text, provenance


def main():
    if not API_KEY:
        print("Set ASHA_API_KEY environment variable")
        sys.exit(1)

    print("=" * 60)
    print("Asha A2A Client")
    print("=" * 60)

    card = discover_agent()
    print()

    queries = [
        "What are the interactions between warfarin and amiodarone?",
        "What are the USPSTF screening recommendations for colorectal cancer?",
        "Synthesize the evidence on GLP-1 agonists and cardiovascular outcomes.",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {query}")
        task = send_query(query)
        response_text, provenance = parse_response(task)

        print(f"Status: {task['status']['state']}")
        print(f"Model: {provenance.get('model', 'N/A')}")
        print(f"Sources: {provenance.get('sources', [])}")
        print(f"Evidence: {provenance.get('evidence_count', 0)} items")
        print(f"Contract: {provenance.get('contract_hash', 'N/A')}")
        print(f"Response: {response_text[:300]}...")
        print()


if __name__ == "__main__":
    main()
