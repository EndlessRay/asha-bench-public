"""Decompose the 25 MedQA paired losses where Asha was wrong and bare Gemini
3.1 Pro Preview was right.

Reviewer flagged asymmetric reporting: we characterize the 66 paired wins
(51 META_CORRECT envelope rescues + 15 KIL evidence substitutions) but not
the 25 paired losses. This script reads the per-question JSONLs in
bench-public/medqa-2026-05-04/results/ and produces a question-level
breakdown.

Available per-question fields: qid, gold, predicted, parsed, correct,
task_gravity, evidence_count, latency_ms, model_tier.

We cannot recover the full response text from the public bundle (the
projection is compact by design), so the mechanism characterization is at
the level of (gravity bucket, model tier, evidence count, latency). That
is enough to test whether losses cluster in any one routing tier or
evidence regime.
"""

from __future__ import annotations
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MEDQA = HERE.parent / "medqa-2026-05-04" / "results"


def load_arm(filename: str) -> dict[str, dict]:
    out = {}
    with open(MEDQA / filename) as f:
        for line in f:
            r = json.loads(line)
            # coerce string booleans to Python booleans (the bundle stores them as strings)
            for k in ("parsed", "correct"):
                if isinstance(r.get(k), str):
                    r[k] = r[k] == "True"
            for k in ("task_gravity",):
                if isinstance(r.get(k), str):
                    r[k] = float(r[k])
            for k in ("evidence_count", "latency_ms"):
                if isinstance(r.get(k), str):
                    r[k] = int(r[k])
            out[r["qid"]] = r
    return out


def main():
    asha = load_arm("asha_per_question.jsonl")
    gem = load_arm("gemini_per_question.jsonl")

    qids = sorted(set(asha) & set(gem))
    print(f"# MedQA paired-loss decomposition (n_paired = {len(qids)})\n")

    # ---- McNemar cells, with parseability of each arm
    cells = Counter()
    for q in qids:
        a, g = asha[q], gem[q]
        if a["correct"] and g["correct"]:
            cells["both_right"] += 1
        elif a["correct"] and not g["correct"]:
            cells["asha_right_gemini_wrong"] += 1
        elif not a["correct"] and g["correct"]:
            cells["asha_wrong_gemini_right"] += 1
        else:
            cells["both_wrong"] += 1
    print("## McNemar cells\n")
    for k in ("both_right", "asha_right_gemini_wrong", "asha_wrong_gemini_right", "both_wrong"):
        print(f"- {k}: {cells[k]}")

    losses = [q for q in qids
              if not asha[q]["correct"] and gem[q]["correct"]]
    print(f"\n## The 25 paired losses (Asha wrong, Gemini right)\n")
    print(f"Total: {len(losses)} questions\n")

    # ---- Characterize each loss
    tier_counts = Counter()
    gravity_counts = Counter()
    parseable_loss = 0
    evidence_counts = []
    latencies = []
    for q in losses:
        a = asha[q]
        if a["parsed"]:
            parseable_loss += 1
        tier_counts[a.get("model_tier", "?")] += 1
        gravity_counts[a["task_gravity"]] += 1
        evidence_counts.append(a["evidence_count"])
        latencies.append(a["latency_ms"])

    print(f"- Asha emitted a parseable wrong letter on **{parseable_loss} of {len(losses)}** losses")
    print(f"  - on the remaining {len(losses)-parseable_loss}, Asha emitted no parseable answer letter\n")

    print("- Routing tier distribution of the 25 losses:")
    for tier, n in sorted(tier_counts.items(), key=lambda kv: -kv[1]):
        print(f"  - {tier}: {n}")

    print("\n- Task-gravity distribution of the 25 losses:")
    for g, n in sorted(gravity_counts.items()):
        print(f"  - g = {g}: {n}")

    print(f"\n- Evidence retrieved (KIL count) on the 25 losses:")
    print(f"  - mean {statistics.fmean(evidence_counts):.1f}, "
          f"median {statistics.median(evidence_counts):.0f}, "
          f"min {min(evidence_counts)}, max {max(evidence_counts)}")

    print(f"\n- Latency on the 25 losses:")
    print(f"  - mean {statistics.fmean(latencies)/1000:.1f} s, "
          f"median {statistics.median(latencies)/1000:.1f} s")

    # ---- Same characterization on the 66 paired wins, for comparison
    wins = [q for q in qids if asha[q]["correct"] and not gem[q]["correct"]]
    win_tier = Counter()
    win_gravity = Counter()
    win_parseable_gemini = 0
    win_evidence = []
    for q in wins:
        a = asha[q]
        g = gem[q]
        if g["parsed"]:
            win_parseable_gemini += 1
        win_tier[a.get("model_tier", "?")] += 1
        win_gravity[a["task_gravity"]] += 1
        win_evidence.append(a["evidence_count"])

    print("\n## Comparison: characterize the 66 paired wins\n")
    print(f"- Gemini emitted a parseable wrong letter on **{win_parseable_gemini} of {len(wins)}** wins")
    print(f"  - on the remaining {len(wins)-win_parseable_gemini}, Gemini emitted no parseable answer (the META_CORRECT rescue mechanism)")
    print("\n- Routing tier distribution of the 66 wins:")
    for tier, n in sorted(win_tier.items(), key=lambda kv: -kv[1]):
        print(f"  - {tier}: {n}")
    print("\n- Task-gravity distribution of the 66 wins:")
    for g, n in sorted(win_gravity.items()):
        print(f"  - g = {g}: {n}")

    # ---- Direct head-to-head on parseable-vs-parseable
    print("\n## Parseable-only subset (the 'fair fight' subset)\n")
    parseable_both = [q for q in qids if asha[q]["parsed"] and gem[q]["parsed"]]
    pa_both_right = sum(1 for q in parseable_both if asha[q]["correct"] and gem[q]["correct"])
    pa_asha = sum(1 for q in parseable_both if asha[q]["correct"] and not gem[q]["correct"])
    pa_gem  = sum(1 for q in parseable_both if not asha[q]["correct"] and gem[q]["correct"])
    pa_both_wrong = sum(1 for q in parseable_both if not asha[q]["correct"] and not gem[q]["correct"])
    print(f"On the {len(parseable_both)} questions where both arms emitted a parseable letter:")
    print(f"- both right: {pa_both_right}")
    print(f"- Asha right, Gemini wrong: {pa_asha}")
    print(f"- Asha wrong, Gemini right: {pa_gem}")
    print(f"- both wrong: {pa_both_wrong}")
    net = pa_asha - pa_gem
    print(f"\nNet paired delta on parseable subset: {net} ({100*net/len(parseable_both):+.2f} pp of parseable subset)")


if __name__ == "__main__":
    main()
