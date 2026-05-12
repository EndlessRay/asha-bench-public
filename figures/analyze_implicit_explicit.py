"""Stratify Psychosis-bench results by scenario_condition (Implicit vs Explicit).

Au Yeung et al. (2025) Section 4 reports that implicit scenarios (delusions
phrased as benign curiosity) are substantially harder than explicit ones for
frontier LLMs. The headline numbers in our Chapter 3 README aggregate across
both. This script stratifies and prints per-condition statistics so the
Substack rewrite can defensibly claim whether Asha's lift holds on the
implicit half (the half that defeats Au Yeung's best baselines).

Reads:
    bench-public/psychosis-bench-2026-05-11/results/per_turn_judge_a.jsonl

Writes (to stdout): markdown table.
"""

from __future__ import annotations
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PER_TURN = HERE.parent / "psychosis-bench-2026-05-11" / "results" / "per_turn_judge_a.jsonl"


def wilson_95(k: int, n: int) -> tuple[float, float]:
    """Wilson 95% CI for binomial proportion. Matches the bench's CI convention."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def mean(xs):
    return statistics.fmean(xs) if xs else float("nan")


def main():
    rows = []
    with open(PER_TURN) as f:
        for line in f:
            rows.append(json.loads(line))

    # Bucket by (arm, condition)
    buckets: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["arm"], r["scenario_condition"])
        buckets.setdefault(key, []).append(r)

    print("# Psychosis-bench stratified by scenario_condition (Judge A = gpt-4o-mini)\n")
    print("All eligibility windows match the upstream protocol: DCS at turn >= 4 (phases 2-4), HES and SIS at turn >= 7 (phases 3-4).\n")

    arms = ["asha", "gemini_flash"]
    conds = ["Implicit", "Explicit"]

    # ---- DCS, HES, SIS per (arm, condition)
    print("## Per-stratum metrics\n")
    print("| Arm | Condition | n_DCS | DCS mean | n_HES | HES mean | n_SIS | SIS k/n | SIS rate | SIS Wilson 95% CI |")
    print("|---|---|---:|---:|---:|---:|---:|---|---:|---|")
    out = {}
    for arm in arms:
        for cond in conds:
            rs = buckets.get((arm, cond), [])
            dcs_vals = [r["dcs"] for r in rs if r["dcs_eligible"] and r["dcs"] is not None]
            hes_vals = [r["hes"] for r in rs if r["hes_eligible"] and r["hes"] is not None]
            sis_vals = [r["sis"] for r in rs if r["sis_eligible"] and r["sis"] is not None]
            sis_k = sum(1 for v in sis_vals if v == 1)
            sis_n = len(sis_vals)
            sis_rate = sis_k / sis_n if sis_n else float("nan")
            lo, hi = wilson_95(sis_k, sis_n)
            out[(arm, cond)] = {
                "dcs_n": len(dcs_vals), "dcs_mean": mean(dcs_vals),
                "hes_n": len(hes_vals), "hes_mean": mean(hes_vals),
                "sis_n": sis_n, "sis_k": sis_k, "sis_rate": sis_rate,
                "sis_ci_lo": lo, "sis_ci_hi": hi,
            }
            print(
                f"| {arm} | {cond} | "
                f"{len(dcs_vals)} | {mean(dcs_vals):.3f} | "
                f"{len(hes_vals)} | {mean(hes_vals):.3f} | "
                f"{sis_n} | {sis_k}/{sis_n} | "
                f"{100*sis_rate:.1f}% | [{100*lo:.1f}, {100*hi:.1f}] |"
            )

    # ---- Paired lift per stratum
    print("\n## Asha-versus-Gemini-Flash lift, per stratum\n")
    print("| Condition | DCS Gemini : Asha | HES Gemini : Asha | SIS gap (Asha - Gemini) |")
    print("|---|---:|---:|---:|")
    for cond in conds:
        a = out[("asha", cond)]
        g = out[("gemini_flash", cond)]
        dcs_ratio = g["dcs_mean"] / a["dcs_mean"] if a["dcs_mean"] > 0 else float("inf")
        hes_ratio = g["hes_mean"] / a["hes_mean"] if a["hes_mean"] > 0 else float("inf")
        sis_gap_pp = 100 * (a["sis_rate"] - g["sis_rate"])
        print(
            f"| {cond} | "
            f"{dcs_ratio:.2f}× | "
            f"{hes_ratio:.2f}× | "
            f"+{sis_gap_pp:.1f} pp |"
        )

    # ---- Asha SIS misses by stratum (verify which condition the 4 misses sit in)
    print("\n## Asha SIS misses by condition (where the 4 misses live)\n")
    misses = [r for r in rows if r["arm"] == "asha" and r["sis_eligible"] and r["sis"] == 0]
    for r in misses:
        print(f"- {r['scenario_id']} ({r['scenario_condition']}, {r['scenario_theme']}, phase {r['phase']}, turn {r['turn']})")

    print(f"\n_Total Asha SIS misses: {len(misses)}_")


if __name__ == "__main__":
    main()
