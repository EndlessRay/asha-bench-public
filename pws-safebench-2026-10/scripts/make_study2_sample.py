#!/usr/bin/env python3
"""Pre-registered expert adjudication subsample: 60 responses, blinded.
10 per arm from Families 1 and 2 (40) + 20 longitudinal turns (5 per arm),
seed 20261003. Writes Docs/preprint/pws-ai-safety-2026-10/review/study2_sample.json.
Experts see the prompt, persona, requirement flags and (for scenarios) the
prior conversation; never the arm, the judge scores or the key-point list."""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT.parents[1] / "Docs" / "preprint" / "pws-ai-safety-2026-10" / "review"
bank = json.loads((ROOT / "data" / "pws_safebench_v1.0.json").read_text(encoding="utf-8"))
items = {i["id"]: i for i in bank["items"]}
scen = {s["id"]: s for s in bank["scenarios"]}
REDACT = re.compile(r"\b(Asha|DNAi(?: Systems)?|askasha(?:\.org)?|ChatGPT|OpenAI|GPT(?:-?\d(?:\.\d)?[a-z]*)?|Claude|Anthropic|Gemini|Google(?: DeepMind)?|Bard)\b", re.I)
resp = {}
for l in (ROOT / "results" / "responses.jsonl").read_text(encoding="utf-8").splitlines():
    if l.strip():
        r = json.loads(l)
        if not r.get("error") and r.get("response"):
            resp[(r["arm"], r["item_id"], r["turn"])] = r
rnd = random.Random(20261003)
arms = ["gpt", "claude", "gemini", "asha"]
out = []
single_ids = [i["id"] for i in bank["items"]]
for a in arms:
    pool = [i for i in single_ids if (a, i, 0) in resp]
    rnd.shuffle(pool)
    for iid in pool[:10]:
        it = items[iid]
        r = resp[(a, iid, 0)]
        guide = []
        if it["requires_escalation"]:
            guide.append(f"This prompt requires escalation: {it['escalation_target']}.")
        if it["requires_refusal"]:
            guide.append(f"This prompt requires a refusal: {it['refusal_scope']}.")
        if it["family"] == "false_premise":
            guide.append(f"Embedded false premise: {it['false_premise']}")
        out.append({"id": f"S2-{len(out) + 1:03d}", "study": 2, "kind": "single", "section_label": "Study 2 adjudication", "context": [], "query": f"[{it['persona']}] {it['prompt']}", "guide": " ".join(guide), "response": REDACT.sub("[SYSTEM]", r["response"]),
                    "_meta": {"arm": a, "item_id": iid, "turn": 0, "requires_escalation": it["requires_escalation"], "requires_refusal": it["requires_refusal"]}})
long_keys = [(sid, t["t"]) for sid, s in scen.items() for t in s["turns"]]
for a in arms:
    pool = [k for k in long_keys if (a, k[0], k[1]) in resp]
    rnd.shuffle(pool)
    # prefer intervention-required turns (4 of 5) to make adjudication informative
    req = [k for k in pool if next(t for t in scen[k[0]]["turns"] if t["t"] == k[1])["intervention_required"]]
    non = [k for k in pool if k not in req]
    chosen = req[:4] + non[:1]
    for sid, tt in chosen:
        sc = scen[sid]
        t = next(x for x in sc["turns"] if x["t"] == tt)
        ctx = []
        for x in sc["turns"]:
            if x["t"] >= tt:
                break
            prev = resp.get((a, sid, x["t"]))
            ctx.append({"role": "user", "text": x["user"]})
            ctx.append({"role": "assistant", "text": REDACT.sub("[SYSTEM]", prev["response"])[:1500] if prev else "[missing]"})
        out.append({"id": f"S2-{len(out) + 1:03d}", "study": 2, "kind": "long", "section_label": "Study 2 adjudication (scenario turn)", "scenario_title": sc["title"], "turn": tt, "intervention_required": t["intervention_required"], "context": ctx[-6:], "query": t["user"], "guide": "", "response": REDACT.sub("[SYSTEM]", resp[(a, sid, tt)]["response"]),
                    "_meta": {"arm": a, "item_id": sid, "turn": tt, "intervention_required": t["intervention_required"]}})
REVIEW.mkdir(exist_ok=True, parents=True)
(REVIEW / "study2_sample.json").write_text(json.dumps({"seed": 20261003, "n": len(out), "items": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print("study2 adjudication sample:", len(out), {a: sum(1 for o in out if o["_meta"]["arm"] == a) for a in arms})
