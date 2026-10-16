"""Independent second computation of the headline numbers in research/analysis/.

Shares no code with council_analyses.py. Differences in path:
  - raw records parsed into plain lists; item scores recomputed from criteria (sum of met points /
    sum of positive points) instead of read from the `score` field;
  - pairing rule, harm counts, severe classification and psychosis counts re-implemented;
  - bootstrap uses numpy's legacy MT19937 RandomState (seed VSEED) and multinomial resampling
    weights (weighted statistics) instead of PCG64 index draws;
  - exact binomial tests from math.comb.
Point estimates must match to rounding; bootstrap bounds within 10% of the interval width
(Monte Carlo error); bootstrap P values must agree on significance at 0.05 and on the Holm decision.
Writes research/analysis/verification.csv; exits 1 on any FAIL.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

PAPER = Path(__file__).resolve().parents[1]
AN = PAPER / "research" / "analysis"
BENCH = Path(os.environ.get("ASHA_BENCH", "/tmp/asha-benchmarks"))
HB = BENCH / "healthbench-5000-2026-09-20"
HARD_FILE = Path(os.environ.get("HB_HARD", "/tmp/hb_hard.jsonl"))
VSEED = 777
B = 4000
GRADERS = ["gpt_4_1", "gpt_5_4", "claude_opus_4_8"]

checks: list[dict] = []


def check(name, main, ver, tol, kind="numeric"):
    if kind == "numeric":
        ok = abs(float(main) - float(ver)) <= tol
    else:
        ok = main == ver
    checks.append(dict(check=name, main=main, verify=ver if kind != "numeric" else round(float(ver), 4),
                       tolerance=tol, status="PASS" if ok else "FAIL"))


def read_csv(name):
    with (AN / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def binom_two_sided(k, n):
    if n == 0:
        return float("nan")
    pk = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pk if p <= pk[k] * (1 + 1e-7)))


def load(arm, g):
    items = {}
    with gzip.open(HB / arm / f"graded_{g}.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            crit = [(c["points"], bool(c["met"]), str(c.get("explanation") or "")) for c in r["rubric_grades"]]
            items[r["prompt_id"]] = crit
    return items


def score(crit):
    pos = sum(p for p, _, _ in crit if p > 0)
    return 100.0 * sum(p for p, m, _ in crit if m) / pos


def bad(crit):
    return any(e.startswith("Parse failed") or e.startswith("Backup parse") for _, _, e in crit)


hard = set()
with HARD_FILE.open(encoding="utf-8") as fh:
    for line in fh:
        hard.add(json.loads(line)["prompt_id"])

rs = np.random.RandomState(VSEED)


def weights(n):
    return rs.multinomial(n, [1.0 / n] * n, size=B).astype(float)


paired_main = {(r["grader"], r["set"]): r for r in read_csv("paired_scores.csv") if r["rule"] == "readout"}
harm_main = {(r["estimator"], r["grader"], r["set"]): r for r in read_csv("harm_estimators.csv") if r["rule"] == "readout"}
harm_all_main = {(r["grader"], r["set"]): r for r in read_csv("harm_estimators.csv") if r["rule"] == "all" and r["estimator"] == "pooled"}
paper_harm_ci = {(r["grader"], r["set"]): r for r in csv.DictReader((PAPER / "research" / "harm_ci.csv").open(encoding="utf-8"))}

grades = {}
vp = {}
for g in GRADERS:
    A, Bm = load("asha-apex-j-frozen", g), load("bare-gpt-6-astra", g)
    grades[g] = (A, Bm)
    for s in ("Standard", "Hard"):
        ids = [k for k in sorted(A) if (s == "Standard" or k in hard) and not bad(A[k]) and not bad(Bm[k])]
        a = [score(A[k]) for k in ids]
        b = [score(Bm[k]) for k in ids]
        d = np.array(a) - np.array(b)
        n = len(ids)
        W = weights(n)
        boot = (W @ d) / n
        lo, hi = np.percentile(boot, [2.5, 97.5])
        m = paired_main[(g, s)]
        width = float(m["ci_boot_hi"]) - float(m["ci_boot_lo"])
        check(f"paired n {g} {s}", m["n_paired"], str(n), 0, "exact")
        check(f"paired asha mean {g} {s}", m["asha_mean"], sum(a) / n, 0.0006)
        check(f"paired bare mean {g} {s}", m["bare_mean"], sum(b) / n, 0.0006)
        check(f"paired diff {g} {s}", m["diff"], d.mean(), 0.0006)
        check(f"paired diff CI low {g} {s}", m["ci_boot_lo"], lo, 0.1 * width)
        check(f"paired diff CI high {g} {s}", m["ci_boot_hi"], hi, 0.1 * width)

        # harm, three estimators
        rows = []
        for k in ids:
            neg = [(p, ma, mb) for (p, ma, _), (_, mb, _) in zip(A[k], Bm[k]) if p < 0]
            if neg:
                rows.append((sum(ma for _, ma, _ in neg), sum(mb for _, _, mb in neg), len(neg)))
        ma = np.array([r[0] for r in rows], float)
        mb = np.array([r[1] for r in rows], float)
        nn = np.array([r[2] for r in rows], float)
        nh = len(rows)
        W = weights(nh)
        est = {
            "pooled": (100 * (ma.sum() - mb.sum()) / nn.sum(), 100 * (W @ ma - W @ mb) / (W @ nn)),
            "item_mean": (100 * ((ma - mb) / nn).mean(), 100 * (W @ ((ma - mb) / nn)) / nh),
            "any_harm": (100 * ((ma > 0).astype(float) - (mb > 0)).mean(), 100 * (W @ ((ma > 0).astype(float) - (mb > 0))) / nh),
        }
        for e, (pt, bt) in est.items():
            hm = harm_main[(e, g, s)]
            width = float(hm["ci_hi"]) - float(hm["ci_lo"])
            lo, hi = np.percentile(bt, [2.5, 97.5])
            pv = min(1.0, 2 * min((np.sum(bt <= 0) + 1) / (B + 1), (np.sum(bt >= 0) + 1) / (B + 1)))
            vp[(e, g, s)] = pv
            check(f"harm {e} n {g} {s}", hm["n_items"], str(nh), 0, "exact")
            check(f"harm {e} diff {g} {s}", hm["diff"], pt, 0.0006)
            check(f"harm {e} CI low {g} {s}", hm["ci_lo"], lo, 0.1 * width)
            check(f"harm {e} CI high {g} {s}", hm["ci_hi"], hi, 0.1 * width)
            mp = float(hm["p_boot"].lstrip("<="))
            check(f"harm {e} significance at 0.05 {g} {s}", str(mp < 0.05), str(pv < 0.05), 0, "exact")

        # rule `all` against the paper's research/harm_ci.csv
        allrows = []
        for k in sorted(A):
            if s == "Hard" and k not in hard:
                continue
            neg = [(ma, mb) for (p, ma, _), (_, mb, _) in zip(A[k], Bm[k]) if p < 0]
            if neg:
                allrows.append((sum(x for x, _ in neg), sum(y for _, y in neg), len(neg)))
        tot = sum(r[2] for r in allrows)
        dall = 100 * (sum(r[0] for r in allrows) - sum(r[1] for r in allrows)) / tot
        check(f"harm pooled rule=all vs research/harm_ci.csv {g} {s}", paper_harm_ci[(g, s)]["diff_pp"], dall, 0.006)
        check(f"harm pooled rule=all main vs verify {g} {s}", harm_all_main[(g, s)]["diff"], dall, 0.0006)

# Holm decisions with the verification P values
for e in ("pooled", "item_mean", "any_harm"):
    keys = [(e, g, s) for g in GRADERS for s in ("Standard", "Hard")]
    ps = [vp[k] for k in keys]
    order = sorted(range(6), key=lambda i: ps[i])
    adj, run = [0.0] * 6, 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (6 - rank) * ps[i]))
        adj[i] = run
    for k, h in zip(keys, adj):
        mh = float(harm_main[k]["p_holm6"])
        check(f"harm {e} Holm decision at 0.05 {k[1]} {k[2]}", str(mh < 0.05), str(h < 0.05), 0, "exact")

# unanimous severe (points <= -9) on Hard, item level, readout rule
common = [k for k in sorted(grades["gpt_4_1"][0]) if k in hard and not any(bad(grades[g][0][k]) or bad(grades[g][1][k]) for g in GRADERS)]
ua = ub = 0
for k in common:
    cls = []
    for g in GRADERS:
        A, Bm = grades[g]
        ao = any(p <= -9 and ma and not mb for (p, ma, _), (_, mb, _) in zip(A[k], Bm[k]))
        bo = any(p <= -9 and mb and not ma for (p, ma, _), (_, mb, _) in zip(A[k], Bm[k]))
        cls.append((ao and not bo, bo and not ao))
    ua += all(c[0] for c in cls)
    ub += all(c[1] for c in cls)
sev = {(r["set"], r["grader"]): r for r in read_csv("tails_severe_discordance.csv") if r["threshold"] == "points<=-9"}
u = sev[("Hard", "unanimous_all_three")]
check("unanimous severe Hard asha-only", u["items_asha_only"], str(ua), 0, "exact")
check("unanimous severe Hard bare-only", u["items_bare_only"], str(ub), 0, "exact")
check("unanimous severe Hard binomial P", u["p_binom_items"], binom_two_sided(ua, ua + ub), 0.0001)

# length-controlled gain point estimate (GPT-4.1 Standard and Hard) via polyfit on independently read lengths
lens = {}
for arm in ("asha-apex-j-frozen", "bare-gpt-6-astra"):
    with gzip.open(HB / arm / "completions.jsonl.gz", "rt", encoding="utf-8") as fh:
        lens[arm] = {r["prompt_id"]: len(r["completion"][-1]["content"]) for r in map(json.loads, fh)}
lc = {(r["grader"], r["set"]): r for r in read_csv("length_controlled_gain.csv")}
A, Bm = grades["gpt_4_1"]
for s in ("Standard", "Hard"):
    ids = [k for k in sorted(A) if s == "Standard" or k in hard]
    x = np.log([lens["asha-apex-j-frozen"][k] / lens["bare-gpt-6-astra"][k] for k in ids])
    y = np.array([score(A[k]) - score(Bm[k]) for k in ids])
    slope, icpt = np.polyfit(x, y, 1)
    check(f"length-controlled intercept gpt_4_1 {s}", lc[("gpt_4_1", s)]["gain_at_equal_length"], icpt, 0.006)
    check(f"length slope gpt_4_1 {s}", lc[("gpt_4_1", s)]["slope_per_log_unit"], slope, 0.006)

# psychosis scenario sign test and CL-bench
per = {}
with (BENCH / "psychosis-bench-2026-05-11/results/per_turn_judge_a.jsonl").open(encoding="utf-8") as fh:
    for line in fh:
        r = json.loads(line)
        if r["sis_eligible"]:
            t = per.setdefault(r["scenario_id"], {}).setdefault(r["arm"], [0, 0])
            t[0] += r["sis"] == 1
            t[1] += 1
w = sum(v["asha"][0] / v["asha"][1] > v["gemini_flash"][0] / v["gemini_flash"][1] for v in per.values())
l_ = sum(v["asha"][0] / v["asha"][1] < v["gemini_flash"][0] / v["gemini_flash"][1] for v in per.values())
ps = [r for r in read_csv("small_sample_tests.csv") if "scenario-level exact sign" in r["test"]][0]
check("psychosis scenario wins", ps["asha_favoured"], str(w), 0, "exact")
check("psychosis scenario losses", ps["comparator_favoured"], str(l_), 0, "exact")
check("psychosis scenario sign-test P", ps["p"], binom_two_sided(w, w + l_), 0.000005)
cl = [r for r in read_csv("small_sample_tests.csv") if r["test"].startswith("CL-bench")][0]
check("CL-bench 18 vs 3 exact P", cl["p"], binom_two_sided(3, 21), 0.00005)

with (AN / "verification.csv").open("w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(checks[0].keys()))
    wr.writeheader()
    wr.writerows(checks)
fails = [c for c in checks if c["status"] == "FAIL"]
print(f"{len(checks)} checks, {len(fails)} FAIL")
for c in fails:
    print("FAIL", c)
sys.exit(1 if fails else 0)
