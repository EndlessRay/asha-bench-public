#!/usr/bin/env python3
"""Judge an Apex-PWS run: same two blinded judges and rubric as v1.1; the
CUTOFF archetype receives the authoritative 2025-2026 fact block prospectively
(both judges' training predates the facts). Resume-safe.

  python3 judge_apexpws.py --bank ../data/pws_safebench_hard_v1.1.json --responses results/dev_C1.jsonl --out results/dev_C1_judgments.jsonl
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from judge_pws_safebench import JudgeA, JudgeB, SEED, parse_json, redact, single_turn_prompt  # noqa: E402
from rejudge_cutoff import GROUND_TRUTH  # noqa: E402


def turn_as_item(sc, t):
    return {"id": f"{sc['id']}:t{t['t']}", "family": "hard", "persona": sc["persona"], "prompt": t["user"], "key_points": t["key_points"], "red_flags": t["red_flags"],
            "requires_escalation": t["requires_escalation"], "escalation_target": t["escalation_target"], "requires_refusal": t["requires_refusal"], "refusal_scope": t["refusal_scope"]}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", required=True)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    bank = json.loads(Path(args.bank).read_text(encoding="utf-8"))
    rubric = bank["rubric"]
    items = {i["id"]: i for i in bank["items"]}
    scen = {s["id"]: s for s in bank["scenarios"]}
    latest = {}
    for l in Path(args.responses).read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if not r.get("error") and r.get("response"):
                latest[(r["item_id"], r["turn"])] = r
    out = Path(args.out)
    done = set()
    if out.exists():
        for l in out.read_text(encoding="utf-8").splitlines():
            if l.strip():
                j = json.loads(l)
                if j.get("scores") and not j.get("error"):
                    done.add((j["judge"], j["item_id"], j["turn"]))
    judges = [JudgeA(), JudgeB()]
    tasks = []
    for (iid, t), r in latest.items():
        if r["family"] == "hard":
            it = items[iid]
            p = single_turn_prompt(it, rubric, redact(r["response"]))
            if it["archetype"] == "CUTOFF":
                p = GROUND_TRUTH + "\n\n" + p
        else:
            sc = scen[iid]
            tt = next(x for x in sc["turns"] if x["t"] == t)
            convo = []
            for x in sc["turns"]:
                if x["t"] >= t:
                    break
                prev = latest.get((iid, x["t"]))
                convo.append(f"[USER t{x['t']}]: {x['user']}\n[ASSISTANT t{x['t']}]: {redact(prev['response']) if prev else '[missing]'}")
            it = turn_as_item(sc, tt)
            it["prompt"] = ("CONVERSATION SO FAR (system names redacted):\n" + "\n\n".join(convo) + f"\n\n[USER t{t} (the turn being scored)]: {tt['user']}") if convo else tt["user"]
            p = single_turn_prompt(it, rubric, redact(r["response"]))
        for jd in judges:
            if (jd.name, iid, t) not in done:
                tasks.append((jd, r, p))
    random.Random(SEED).shuffle(tasks)
    print(f"responses={len(latest)} pending={len(tasks)}")
    f = open(out, "a", encoding="utf-8")
    lock = asyncio.Lock()

    async def run(jd, r, p):
        row = {"judge": jd.name, "judge_model": jd.model, "arm": r["arm"], "item_id": r["item_id"], "family": r["family"], "archetype": r["archetype"], "turn": r["turn"], "prompt_sha": hashlib.sha256(p.encode()).hexdigest()[:12], "scores": None, "rationale": None, "error": None}
        try:
            raw = await jd.judge(p)
            js = parse_json(raw)
            if js:
                row["rationale"] = js.pop("rationale", None)
                row["scores"] = js
            else:
                row["error"] = "unparseable"
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
