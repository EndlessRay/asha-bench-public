#!/usr/bin/env python3
"""Dual blinded judging for PWS-SafeBench Hard v1.1 (reuses the v1.0 judges,
rubric prompt, redaction and shuffling). PRESS turns are judged with the
single-turn rubric using that turn's key points and red flags, with the
redacted conversation so far shown above the response."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from judge_pws_safebench import JudgeA, JudgeB, SEED, parse_json, redact, single_turn_prompt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BANK = json.loads((ROOT / "data" / "pws_safebench_hard_v1.1.json").read_text(encoding="utf-8"))


def turn_as_item(sc: dict, t: dict) -> dict:
    return {"id": f"{sc['id']}:t{t['t']}", "family": "hard", "persona": sc["persona"], "prompt": t["user"],
            "key_points": t["key_points"], "red_flags": t["red_flags"], "requires_escalation": t["requires_escalation"],
            "escalation_target": t["escalation_target"], "requires_refusal": t["requires_refusal"], "refusal_scope": t["refusal_scope"]}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", default=str(ROOT / "results_hard" / "responses.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "results_hard" / "judgments.jsonl"))
    args = ap.parse_args()
    rubric = BANK["rubric"]
    items = {i["id"]: i for i in BANK["items"]}
    scen = {s["id"]: s for s in BANK["scenarios"]}
    latest = {}
    for l in open(args.responses, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if not r.get("error") and r.get("response"):
                latest[(r["arm"], r["item_id"], r["turn"])] = r
    out_path = Path(args.out)
    done = set()
    if out_path.exists():
        for l in out_path.read_text(encoding="utf-8").splitlines():
            if l.strip():
                j = json.loads(l)
                if j.get("scores") and not j.get("error"):
                    done.add((j["judge"], j["arm"], j["item_id"], j["turn"]))
    judges = [JudgeA(), JudgeB()]
    tasks = []
    for k, r in latest.items():
        if r["family"] == "hard":
            it = dict(items[r["item_id"]])
            p = single_turn_prompt(it, rubric, redact(r["response"]))
        else:
            sc = scen[r["item_id"]]
            t = next(t for t in sc["turns"] if t["t"] == r["turn"])
            convo = []
            for tt in sc["turns"]:
                if tt["t"] >= r["turn"]:
                    break
                prev = latest.get((r["arm"], r["item_id"], tt["t"]))
                convo.append(f"[USER t{tt['t']}]: {tt['user']}\n[ASSISTANT t{tt['t']}]: {redact(prev['response']) if prev else '[missing]'}")
            it = turn_as_item(sc, t)
            it["prompt"] = ("CONVERSATION SO FAR (system names redacted):\n" + "\n\n".join(convo) + f"\n\n[USER t{t['t']} (the turn being scored)]: {t['user']}") if convo else t["user"]
            p = single_turn_prompt(it, rubric, redact(r["response"]))
        for jd in judges:
            if (jd.name, r["arm"], r["item_id"], r["turn"]) not in done:
                tasks.append((jd, r, p))
    random.Random(SEED).shuffle(tasks)
    print(f"responses={len(latest)} pending_judge_calls={len(tasks)} done={len(done)}")
    lock = asyncio.Lock()
    f = open(out_path, "a", encoding="utf-8")

    async def run(jd, r, p):
        row = {"judge": jd.name, "judge_model": jd.model, "arm": r["arm"], "item_id": r["item_id"], "family": r["family"], "archetype": r["archetype"], "turn": r["turn"], "prompt_sha": hashlib.sha256(p.encode()).hexdigest()[:12], "scores": None, "rationale": None, "raw": None, "error": None}
        try:
            raw = await jd.judge(p)
            row["raw"] = raw[:4000]
            js = parse_json(raw)
            if not js:
                row["error"] = "unparseable"
            else:
                row["rationale"] = js.pop("rationale", None)
                row["scores"] = js
        except Exception as exc:
            row["error"] = str(exc)[:300]
        async with lock:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()

    for i in range(0, len(tasks), 40):
        await asyncio.gather(*(run(*t) for t in tasks[i:i + 40]))
        print(f"  {min(i + 40, len(tasks))}/{len(tasks)}", flush=True)
    f.close()


if __name__ == "__main__":
    asyncio.run(main())
