"""
Asha A/B Evaluation Harness
============================
Compare Asha against your current medical AI provider on a representative
question set. Records latency, evidence count, response text, and source
collections from each side so you can review side-by-side.

Usage:
    1. Get a free Asha key (50 queries/month, no credit card):
       curl -X POST https://api.askasha.org/api/a2a/signup \\
         -H "Content-Type: application/json" \\
         -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

    2. Edit the `query_other_api` function below to match your current
       provider's auth scheme and request format.

    3. Put your evaluation questions in `eval_set.txt`, one per line.

    4. Run:
       ASHA_API_KEY=... OTHER_API_KEY=... python evaluation.py

Output: `ab_results_<timestamp>.json` with one record per question, both
sides side-by-side. Open in any spreadsheet or notebook for review.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ASHA_BASE = "https://api.askasha.org"
ASHA_KEY = os.getenv("ASHA_API_KEY", "")
OTHER_API_BASE = os.getenv("OTHER_API_BASE", "")
OTHER_API_KEY = os.getenv("OTHER_API_KEY", "")
EVAL_SET = Path(os.getenv("EVAL_SET", "eval_set.txt"))


def query_asha(question: str) -> dict[str, Any]:
    """Send one question to Asha. Returns timing + response + provenance."""
    t0 = time.perf_counter()
    r = requests.post(
        f"{ASHA_BASE}/a2a/v1/message:send",
        headers={"Authorization": f"Bearer {ASHA_KEY}", "Content-Type": "application/json"},
        json={
            "message": {"role": "user", "parts": [{"text": question}]},
            "metadata": {"agent_id": "asha"},
        },
        timeout=120,
    )
    elapsed = time.perf_counter() - t0
    r.raise_for_status()
    task = r.json().get("task", {})

    response_text = ""
    provenance: dict[str, Any] = {}
    for artifact in task.get("artifacts", []):
        if artifact.get("name") == "response" and artifact.get("parts"):
            response_text = artifact["parts"][0].get("text", "")
        elif artifact.get("name") == "provenance" and artifact.get("parts"):
            provenance = artifact["parts"][0].get("data", {})

    return {
        "provider": "asha",
        "latency_s": round(elapsed, 3),
        "state": task.get("status", {}).get("state"),
        "response": response_text,
        "response_len": len(response_text),
        "evidence_count": provenance.get("evidence_count", 0),
        "sources": provenance.get("sources", []),
        "predicate_scope": provenance.get("predicate_scope", []),
        "contract_hash": provenance.get("contract_hash"),
    }


def query_other_api(question: str) -> dict[str, Any]:
    """
    EDIT THIS FUNCTION to match your current provider.

    Most medical AI APIs are OpenAI-compatible chat or simple POST endpoints.
    Replace the body below with whatever your current provider expects.
    """
    if not OTHER_API_BASE or not OTHER_API_KEY:
        return {"provider": "other", "skipped": True, "reason": "OTHER_API_BASE / OTHER_API_KEY not set"}

    t0 = time.perf_counter()
    r = requests.post(
        f"{OTHER_API_BASE}/v1/chat/completions",
        headers={"Authorization": f"Bearer {OTHER_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": os.getenv("OTHER_API_MODEL", "default"),
            "messages": [{"role": "user", "content": question}],
        },
        timeout=120,
    )
    elapsed = time.perf_counter() - t0
    r.raise_for_status()
    body = r.json()
    response_text = ""
    if "choices" in body and body["choices"]:
        response_text = body["choices"][0].get("message", {}).get("content", "")

    return {
        "provider": "other",
        "latency_s": round(elapsed, 3),
        "response": response_text,
        "response_len": len(response_text),
        "evidence_count": None,
        "sources": [],
        "predicate_scope": [],
        "contract_hash": None,
    }


def falsify_with_feng(claim: str) -> dict[str, Any]:
    """
    Optional: send any single claim from either response through FENG to get
    a Popperian falsification verdict (FALSIFIED / WEAKENED / CONDITIONAL /
    UNFALSIFIED) with E-value and evidence_for / evidence_against.

    FENG uses a JWT (login-issued) — not the A2A API key. See feng-a2a repo
    for the public token-bound usage. For an offline review pass, leave this
    disabled and review responses by hand.
    """
    return {"skipped": True, "note": "Enable FENG manually with a logged-in JWT"}


def load_questions() -> list[str]:
    if not EVAL_SET.exists():
        sys.exit(
            f"Eval set not found at {EVAL_SET}.\n"
            "Create it as a plain text file, one question per line. Mix easy and hard:\n"
            "  - 'What is the mechanism of action of metformin?'\n"
            "  - 'Differential diagnosis for new-onset atrial fibrillation in a 32yo F with palpitations and weight loss?'\n"
            "  - 'Is co-administration of amiodarone and warfarin contraindicated, or just dose-adjusted?'\n"
        )
    return [line.strip() for line in EVAL_SET.read_text().splitlines() if line.strip() and not line.startswith("#")]


def main():
    if not ASHA_KEY:
        sys.exit("Set ASHA_API_KEY (free key: POST https://api.askasha.org/api/a2a/signup)")

    questions = load_questions()
    print(f"Running {len(questions)} questions across both providers...")

    results = []
    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q[:80]}...")
        record = {"question": q}
        try:
            record["asha"] = query_asha(q)
            print(f"  asha     {record['asha']['latency_s']:>6}s  evidence={record['asha']['evidence_count']:>3}  sources={len(record['asha']['sources'])}")
        except Exception as exc:
            record["asha"] = {"provider": "asha", "error": str(exc)}
            print(f"  asha     ERROR: {exc}")

        try:
            record["other"] = query_other_api(q)
            other = record["other"]
            if other.get("skipped"):
                print(f"  other    skipped ({other['reason']})")
            else:
                print(f"  other    {other['latency_s']:>6}s  len={other['response_len']}")
        except Exception as exc:
            record["other"] = {"provider": "other", "error": str(exc)}
            print(f"  other    ERROR: {exc}")

        results.append(record)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "asha_base": ASHA_BASE,
        "other_base": OTHER_API_BASE or "(not configured)",
        "n_questions": len(questions),
        "results": results,
    }

    summary = summarize(results)
    out["summary"] = summary

    fname = f"ab_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(fname).write_text(json.dumps(out, indent=2))
    print(f"\nSaved: {fname}")
    print("\n--- Summary ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")


def summarize(results: list[dict]) -> dict[str, Any]:
    asha_latencies = [r["asha"]["latency_s"] for r in results if "latency_s" in r.get("asha", {})]
    other_latencies = [r["other"]["latency_s"] for r in results if "latency_s" in r.get("other", {})]
    asha_evidence = [r["asha"]["evidence_count"] for r in results if r.get("asha", {}).get("evidence_count") is not None]

    def stats(xs: list) -> dict:
        if not xs:
            return {"n": 0}
        sxs = sorted(xs)
        return {
            "n": len(xs),
            "p50": sxs[len(sxs) // 2],
            "p95": sxs[int(len(sxs) * 0.95)] if len(sxs) >= 20 else sxs[-1],
            "max": max(xs),
        }

    return {
        "asha_latency_s": stats(asha_latencies),
        "other_latency_s": stats(other_latencies),
        "asha_evidence_per_response": stats(asha_evidence),
        "asha_provenance_coverage": f"{len(asha_evidence)}/{len(results)} responses",
    }


if __name__ == "__main__":
    main()
