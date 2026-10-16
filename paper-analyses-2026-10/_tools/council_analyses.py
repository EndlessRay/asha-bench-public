"""Council recomputations for the nonmaleficence manuscript, from public per-item data.

Inputs
  ASHA_BENCH  clone of EndlessRay/asha-benchmarks (default /tmp/asha-benchmarks)
              healthbench-5000-2026-09-20/{asha-apex-j-frozen,bare-gpt-6-astra}/
                graded_{gpt_4_1,gpt_5_4,claude_opus_4_8}.jsonl.gz, completions.jsonl.gz
              healthbench-5000-2026-09-20/readouts/official_readout_hb5000_{standard,hard}.json
              psychosis-bench-2026-05-11/results/per_turn_judge_a.jsonl
              medqa-2026-05-04/results/{asha,gemini}_per_question.jsonl
  HB_HARD     official HealthBench Hard ids (default /tmp/hb_hard.jsonl; the public file
              https://openaipublic.blob.core.windows.net/simple-evals/healthbench/hard_2025-05-08-21-00-10.jsonl)

Outputs  research/analysis/*.csv and research/analysis/SUMMARY.md

Methods (also written into SUMMARY.md)
  Item score       the `score` field of each graded record: sum of points of met criteria divided by
                   the sum of positive points (unclipped; can be negative). Reported x100.
  Failed grade     a criterion whose explanation starts with "Parse failed" (no verdict; stored met=false)
                   or "Backup parse" (verdict recovered by the fallback parser). Only Claude Opus 4.8
                   grades contain them.
  Pairing rules    readout   (PRIMARY) drop the whole item from both arms if either arm's grade of that
                             item contains a failed criterion. This is the rule the official readouts
                             used; it reproduces their n and differences exactly.
                   criterion keep every item; drop "Parse failed" criteria from both arms and rescore
                             the item from the remaining criteria; keep "Backup parse" verdicts.
                             Items left with no positive criterion are dropped.
                   all       keep every item and every stored verdict (the rule of _tools/harm_ci.py).
                   GPT-4.1 and GPT-5.4 grades contain no failed criteria, so all three rules coincide.
  Bootstrap        item-level (cluster) percentile bootstrap; paired: the same resampled item set
                   is used for both arms. Seed SEED; each contrast has its own SeedSequence keyed by
                   the contrast labels, so results do not depend on execution order.
  Bootstrap P      two-sided, min(1, 2 * min((#{b<=0}+1)/(B+1), (#{b>=0}+1)/(B+1))).
  Harm estimators  over items with >=1 negative-point criterion (after the pairing rule):
                   pooled     100 * (sum met_A - sum met_B) / sum n_neg     (paper's estimator)
                   item_mean  100 * mean_i(met_A_i/n_i - met_B_i/n_i)
                   any_harm   100 * mean_i(1[met_A_i>0] - 1[met_B_i>0])
                   severity   mean_i(negative points met by A - by B), in rubric points (supplementary)
                   Holm and Bonferroni across the 6 grader-by-set contrasts, within estimator and rule.
  Criteria matched across arms and graders by position (rubrics are identical; 575 items carry
  duplicate truncated criterion text, so text matching would collapse them).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
import platform
import subprocess
import zlib
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

PAPER = Path(__file__).resolve().parents[1]
OUT = PAPER / "research" / "analysis"
BENCH = Path(os.environ.get("ASHA_BENCH", "/tmp/asha-benchmarks"))
HB = BENCH / "healthbench-5000-2026-09-20"
HARD_FILE = Path(os.environ.get("HB_HARD", "/tmp/hb_hard.jsonl"))

SEED = 20261016
B_CI = 10000
B_HARM = 20000
CHUNK = 500
GRADERS = ("gpt_4_1", "gpt_5_4", "claude_opus_4_8")
PRETTY = {"gpt_4_1": "GPT-4.1 (official)", "gpt_5_4": "GPT-5.4 (low)", "claude_opus_4_8": "Claude Opus 4.8"}
ARM_A, ARM_B = "asha-apex-j-frozen", "bare-gpt-6-astra"
FAILED = ("Parse failed", "Backup parse")
NOVERDICT = ("Parse failed",)
SEVERE_THRESHOLDS = (-7, -9, -10)
SEVERE = -9
RULES = ("readout", "criterion", "all")
PRIMARY = "readout"
SETS = ("Standard", "Hard")


# ----------------------------------------------------------------------------- helpers

def rng_for(*keys) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SEED] + [zlib.crc32(str(k).encode()) for k in keys]))


def chunks(rng: np.random.Generator, n: int, B: int):
    done = 0
    while done < B:
        c = min(CHUNK, B - done)
        yield rng.integers(0, n, (c, n))
        done += c


def pct(boot: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(lo), float(hi)


def boot_p(boot: np.ndarray) -> float:
    B = len(boot)
    return min(1.0, 2 * min((np.sum(boot <= 0) + 1) / (B + 1), (np.sum(boot >= 0) + 1) / (B + 1)))


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj


def binom_p(k: int, n: int) -> float:
    return float(stats.binomtest(k, n, 0.5).pvalue) if n else float("nan")


def kappa(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    po = float((x == y).mean())
    px, py = x.mean(), y.mean()
    pe = px * py + (1 - px) * (1 - py)
    return float((po - pe) / (1 - pe)), po


def r2(x, nd=2):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


def fp(p: float) -> str:
    return "" if p is None or (isinstance(p, float) and math.isnan(p)) else f"{p:.2g}"


def dump(name: str, rows: list[dict]) -> None:
    with (OUT / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ----------------------------------------------------------------------------- load

def load_grades(arm: str, g: str) -> dict:
    out = {}
    with gzip.open(HB / arm / f"graded_{g}.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            rg = r["rubric_grades"]
            expl = [str(c.get("explanation") or "") for c in rg]
            out[r["prompt_id"]] = dict(
                score=float(r["score"]),
                pts=np.array([c["points"] for c in rg], dtype=float),
                met=np.array([bool(c["met"]) for c in rg]),
                failed=np.array([e.startswith(FAILED) for e in expl]),
                noverdict=np.array([e.startswith(NOVERDICT) for e in expl]),
            )
    return out


def load_lengths(arm: str) -> dict:
    with gzip.open(HB / arm / "completions.jsonl.gz", "rt", encoding="utf-8") as fh:
        return {r["prompt_id"]: len(r["completion"][-1]["content"]) for r in map(json.loads, fh)}


print("loading grades ...")
G = {arm: {g: load_grades(arm, g) for g in GRADERS} for arm in (ARM_A, ARM_B)}
IDS = sorted(G[ARM_A]["gpt_4_1"])
assert all(set(G[a][g]) == set(IDS) for a in G for g in GRADERS)
N = len(IDS)
with HARD_FILE.open(encoding="utf-8") as fh:
    HARD = {json.loads(l)["prompt_id"] for l in fh}
assert len(HARD) == 1000 and HARD <= set(IDS)
IS_HARD = np.array([k in HARD for k in IDS])
SETMASK = {"Standard": np.ones(N, bool), "Hard": IS_HARD}
_la, _lb = load_lengths(ARM_A), load_lengths(ARM_B)
LEN_A = np.array([_la[k] for k in IDS], dtype=float)
LEN_B = np.array([_lb[k] for k in IDS], dtype=float)
LOGR = np.log(LEN_A / LEN_B)


class View:
    """Per-item arrays for one grader under one pairing rule (aligned with IDS)."""

    def __init__(self, g: str, rule: str):
        A, Bm = G[ARM_A][g], G[ARM_B][g]
        self.mask = np.ones(N, bool)
        self.sa = np.zeros(N)
        self.sb = np.zeros(N)
        self.nneg = np.zeros(N, int)
        self.ma = np.zeros(N, int)
        self.mb = np.zeros(N, int)
        self.wa = np.zeros(N)
        self.wb = np.zeros(N)
        self.sev_item = {t: (np.zeros(N, bool), np.zeros(N, bool)) for t in SEVERE_THRESHOLDS}
        self.sev_crit = {t: (np.zeros(N, int), np.zeros(N, int)) for t in SEVERE_THRESHOLDS}
        self.crit_keep = []
        for i, k in enumerate(IDS):
            a, b = A[k], Bm[k]
            pts = a["pts"]
            keep = np.ones(len(pts), bool)
            if rule == "readout" and (a["failed"].any() or b["failed"].any()):
                self.mask[i] = False
            if rule == "criterion":
                keep = ~(a["noverdict"] | b["noverdict"])
                pos = pts[keep & (pts > 0)].sum()
                if pos > 0:
                    self.sa[i] = 100 * pts[keep & a["met"]].sum() / pos
                    self.sb[i] = 100 * pts[keep & b["met"]].sum() / pos
                else:
                    self.mask[i] = False
            else:
                self.sa[i], self.sb[i] = 100 * a["score"], 100 * b["score"]
            self.crit_keep.append(keep)
            neg = keep & (pts < 0)
            self.nneg[i] = neg.sum()
            self.ma[i] = (neg & a["met"]).sum()
            self.mb[i] = (neg & b["met"]).sum()
            self.wa[i] = -pts[neg & a["met"]].sum()
            self.wb[i] = -pts[neg & b["met"]].sum()
            for t in SEVERE_THRESHOLDS:
                sev = keep & (pts <= t)
                ao = sev & a["met"] & ~b["met"]
                bo = sev & b["met"] & ~a["met"]
                self.sev_crit[t][0][i], self.sev_crit[t][1][i] = ao.sum(), bo.sum()
                self.sev_item[t][0][i] = ao.any() and not bo.any()
                self.sev_item[t][1][i] = bo.any() and not ao.any()


print("building views ...")
V = {(g, rule): View(g, rule) for g in GRADERS for rule in RULES}
OUT.mkdir(parents=True, exist_ok=True)
S: dict = {}  # headline numbers for SUMMARY.md


# ----------------------------------------------------------------------------- (a) paired scores

def paired(a: np.ndarray, b: np.ndarray, rng) -> dict:
    d = a - b
    n = len(d)
    boot = np.concatenate([d[idx].mean(1) for idx in chunks(rng, n, B_CI)])
    lo, hi = pct(boot)
    se = d.std(ddof=1) / math.sqrt(n)
    tc = stats.t.ppf(0.975, n - 1)
    w, l_, ti = int((d > 0).sum()), int((d < 0).sum()), int((d == 0).sum())
    return dict(n_paired=n, asha_mean=a.mean(), bare_mean=b.mean(), diff=d.mean(), ci_boot_lo=lo, ci_boot_hi=hi,
                ci_t_lo=d.mean() - tc * se, ci_t_hi=d.mean() + tc * se, p_t=float(stats.ttest_rel(a, b).pvalue),
                wins=w, losses=l_, ties=ti, p_sign=binom_p(w, w + l_))


print("(a) paired scores ...")
paired_rows = []
for g in GRADERS:
    for s in SETS:
        for rule in RULES:
            v = V[(g, rule)]
            m = v.mask & SETMASK[s]
            r = paired(v.sa[m], v.sb[m], rng_for("paired", g, s, rule))
            row = dict(grader=g, set=s, rule=rule, primary="yes" if rule == PRIMARY else "no")
            row.update({k: (r2(x, 3) if isinstance(x, float) and not k.startswith("p_") else x) for k, x in r.items()})
            row["p_t"], row["p_sign"] = fp(r["p_t"]), fp(r["p_sign"])
            paired_rows.append(row)
            S[("paired", g, s, rule)] = r
dump("paired_scores", paired_rows)

# Opus n reconciliation against the official readouts
recon_rows = []
for s, fname in (("Standard", "official_readout_hb5000_standard.json"), ("Hard", "official_readout_hb5000_hard.json")):
    ro = json.loads((HB / "readouts" / fname).read_text(encoding="utf-8"))["graders"]["claude_opus_4_8"]
    A, Bm = G[ARM_A]["claude_opus_4_8"], G[ARM_B]["claude_opus_4_8"]
    ids = [k for k in IDS if s == "Standard" or k in HARD]
    fa = {k for k in ids if A[k]["failed"].any()}
    fb = {k for k in ids if Bm[k]["failed"].any()}
    pa = {k for k in ids if A[k]["noverdict"].any()}
    pb = {k for k in ids if Bm[k]["noverdict"].any()}
    asha_only_excl = [100 * A[k]["score"] for k in ids if k not in fa]
    paired_r = S[("paired", "claude_opus_4_8", s, "readout")]
    allr = S[("paired", "claude_opus_4_8", s, "all")]
    recon_rows.append(dict(
        set=s, items=len(ids),
        asha_items_parse_failed=len(pa), bare_items_parse_failed=len(pb),
        asha_items_failed_any=len(fa), bare_items_failed_any=len(fb), union_failed_any=len(fa | fb),
        asha_n_asha_only_exclusion=len(asha_only_excl), asha_mean_asha_only_exclusion=r2(np.mean(asha_only_excl), 3),
        readout_arm_n=ro["arm"]["raw"]["n"], readout_arm_score=r2(ro["arm"]["raw"]["score"], 3),
        paired_n_readout_rule=paired_r["n_paired"], paired_asha_mean=r2(paired_r["asha_mean"], 3),
        paired_bare_mean=r2(paired_r["bare_mean"], 3), paired_diff=r2(paired_r["diff"], 3),
        readout_paired_n=ro["paired"]["raw"]["n"], readout_paired_diff=r2(ro["paired"]["raw"]["mean_diff_pp"], 3),
        readout_comparator_score=r2(ro["comparator"]["raw"]["score"], 3),
        reproduces_readout="yes" if (paired_r["n_paired"] == ro["paired"]["raw"]["n"]
                                     and abs(paired_r["diff"] - ro["paired"]["raw"]["mean_diff_pp"]) < 1e-9) else "NO",
        n_all_items=allr["n_paired"], diff_all_items=r2(allr["diff"], 3),
        asha_mean_all_items=r2(allr["asha_mean"], 3), bare_mean_all_items=r2(allr["bare_mean"], 3),
    ))
dump("opus_pairing_reconciliation", recon_rows)


# ----------------------------------------------------------------------------- (b) harm proxy

def harm_stats(ma, mb, nn, wa, wb):
    return dict(
        pooled=(100 * ma.sum() / nn.sum(), 100 * mb.sum() / nn.sum()),
        item_mean=(100 * (ma / nn).mean(), 100 * (mb / nn).mean()),
        any_harm=(100 * (ma > 0).mean(), 100 * (mb > 0).mean()),
        severity=(wa.mean(), wb.mean()),
    )


ESTIMATORS = ("pooled", "item_mean", "any_harm", "severity")
print("(b) harm ...")
harm_rows = []
for rule in RULES:
    for g in GRADERS:
        for s in SETS:
            v = V[(g, rule)]
            m = v.mask & SETMASK[s] & (v.nneg > 0)
            ma, mb, nn, wa, wb = v.ma[m], v.mb[m], v.nneg[m], v.wa[m], v.wb[m]
            n = len(nn)
            pt = harm_stats(ma, mb, nn, wa, wb)
            boots = {e: [] for e in ESTIMATORS}
            for idx in chunks(rng_for("harm", g, s, rule), n, B_HARM):
                A_, B_, N_ = ma[idx], mb[idx], nn[idx]
                boots["pooled"].append(100 * (A_.sum(1) - B_.sum(1)) / N_.sum(1))
                boots["item_mean"].append(100 * ((A_ - B_) / N_).mean(1))
                boots["any_harm"].append(100 * ((A_ > 0).astype(int) - (B_ > 0)).mean(1))
                boots["severity"].append((wa[idx] - wb[idx]).mean(1))
            for e in ESTIMATORS:
                b = np.concatenate(boots[e])
                lo, hi = pct(b)
                harm_rows.append(dict(rule=rule, primary="yes" if rule == PRIMARY else "no", estimator=e, grader=g,
                                      set=s, n_items=n, asha=pt[e][0], bare=pt[e][1], diff=pt[e][0] - pt[e][1],
                                      ci_lo=lo, ci_hi=hi, p_boot=boot_p(b), B=B_HARM))
for rule in RULES:
    for e in ESTIMATORS:
        grp = [r for r in harm_rows if r["rule"] == rule and r["estimator"] == e]
        hp = holm([r["p_boot"] for r in grp])
        for r, h in zip(grp, hp):
            r["p_holm6"] = h
            r["p_bonf6"] = min(1.0, 6 * r["p_boot"])
            r["bonf_ci_note"] = "significant after Bonferroni" if r["p_bonf6"] < 0.05 else "not significant after Bonferroni"
for r in harm_rows:
    S[("harm", r["rule"], r["estimator"], r["grader"], r["set"])] = dict(r)
    for k in ("asha", "bare", "diff", "ci_lo", "ci_hi"):
        r[k] = r2(r[k], 3)
    floor = 2 / (B_HARM + 1)
    for k in ("p_boot", "p_holm6", "p_bonf6"):
        r[k] = f"<={floor:.1g}" if k == "p_boot" and r[k] <= floor + 1e-15 else fp(r[k])
dump("harm_estimators", harm_rows)


# ----------------------------------------------------------------------------- (c) tails

print("(c) tails ...")
tail_rows = []
for g in GRADERS:
    for s in SETS:
        v = V[(g, PRIMARY)]
        m = v.mask & SETMASK[s]
        a, b = v.sa[m], v.sb[m]
        d = a - b
        n = len(d)
        k5 = max(1, int(round(0.05 * n)))
        lose, win = int((d <= -50).sum()), int((d >= 50).sum())
        q = np.percentile(d, [1, 5, 50, 95, 99])
        tail_rows.append(dict(grader=g, set=s, n=n, items_lost_ge50=lose, share_lost_ge50_pct=r2(100 * lose / n),
                              items_won_ge50=win, share_won_ge50_pct=r2(100 * win / n), p_binom_lost_vs_won=fp(binom_p(lose, lose + win)),
                              worst5pct_k=k5, worst5pct_mean_asha=r2(np.sort(a)[:k5].mean()), worst5pct_mean_bare=r2(np.sort(b)[:k5].mean()),
                              diff_p1=r2(q[0], 1), diff_p5=r2(q[1], 1), diff_p50=r2(q[2], 1), diff_p95=r2(q[3], 1), diff_p99=r2(q[4], 1)))
        S[("tails", g, s)] = tail_rows[-1]
dump("tails_scores", tail_rows)

sev_rows = []
COMMON = np.logical_and.reduce([V[(g, PRIMARY)].mask for g in GRADERS])
for t in SEVERE_THRESHOLDS:
    for s in SETS:
        for g in GRADERS:
            v = V[(g, PRIMARY)]
            m = v.mask & SETMASK[s]
            ia, ib = int(v.sev_item[t][0][m].sum()), int(v.sev_item[t][1][m].sum())
            ca, cb = int(v.sev_crit[t][0][m].sum()), int(v.sev_crit[t][1][m].sum())
            sev_rows.append(dict(threshold=f"points<={t}", set=s, grader=g, n_items=int(m.sum()),
                                 items_asha_only=ia, items_bare_only=ib, p_binom_items=fp(binom_p(ia, ia + ib)),
                                 crit_asha_only=ca, crit_bare_only=cb, p_binom_crit_unclustered=fp(binom_p(ca, ca + cb))))
        m = COMMON & SETMASK[s]
        ua = int(np.logical_and.reduce([V[(g, PRIMARY)].sev_item[t][0] for g in GRADERS])[m].sum())
        ub = int(np.logical_and.reduce([V[(g, PRIMARY)].sev_item[t][1] for g in GRADERS])[m].sum())
        sev_rows.append(dict(threshold=f"points<={t}", set=s, grader="unanimous_all_three", n_items=int(m.sum()),
                             items_asha_only=ua, items_bare_only=ub, p_binom_items=fp(binom_p(ua, ua + ub)),
                             crit_asha_only="", crit_bare_only="", p_binom_crit_unclustered=""))
dump("tails_severe_discordance", sev_rows)
for r in sev_rows:
    S[("sev", r["threshold"], r["set"], r["grader"])] = r

swing_rows = []
for s in SETS:
    m = COMMON & SETMASK[s]
    D = np.vstack([(V[(g, PRIMARY)].sa - V[(g, PRIMARY)].sb)[m] for g in GRADERS])
    for th in (25, 50):
        worse, better = int((D <= -th).all(0).sum()), int((D >= th).all(0).sum())
        swing_rows.append(dict(set=s, n_items=int(m.sum()), threshold_points=th, unanimous_asha_worse=worse,
                               unanimous_asha_better=better, p_binom=fp(binom_p(worse, worse + better))))
dump("tails_unanimous_swings", swing_rows)


# ----------------------------------------------------------------------------- (d) length tertiles

print("(d) length tertiles ...")
len_rows, lencorr_rows = [], []
for s in SETS:
    sm = SETMASK[s]
    q1, q2 = np.quantile(LOGR[sm], [1 / 3, 2 / 3])
    terc = np.where(LOGR <= q1, 0, np.where(LOGR <= q2, 1, 2))
    for g in GRADERS:
        v = V[(g, PRIMARY)]
        for t in range(3):
            m = v.mask & sm & (terc == t)
            d = v.sa[m] - v.sb[m]
            gb = np.concatenate([d[idx].mean(1) for idx in chunks(rng_for("lt_gain", g, s, t), len(d), B_CI)])
            mh = m & (v.nneg > 0)
            ma, mb, nn = v.ma[mh], v.mb[mh], v.nneg[mh]
            hb = np.concatenate([100 * (ma[idx].sum(1) - mb[idx].sum(1)) / nn[idx].sum(1)
                                 for idx in chunks(rng_for("lt_harm", g, s, t), len(nn), B_CI)])
            ratio = np.exp(LOGR[m])
            len_rows.append(dict(set=s, grader=g, tertile=t + 1, n_items=int(m.sum()), ratio_min=r2(ratio.min()),
                                 ratio_median=r2(np.median(ratio)), ratio_max=r2(ratio.max()),
                                 score_gain=r2(d.mean()), gain_ci_lo=r2(pct(gb)[0]), gain_ci_hi=r2(pct(gb)[1]),
                                 n_harm_items=int(mh.sum()), harm_pooled_diff=r2(100 * (ma.sum() - mb.sum()) / nn.sum()),
                                 harm_ci_lo=r2(pct(hb)[0]), harm_ci_hi=r2(pct(hb)[1])))
            S[("lt", s, g, t + 1)] = len_rows[-1]
        m = v.mask & sm
        mh = m & (v.nneg > 0)
        rg = stats.spearmanr(LOGR[m], v.sa[m] - v.sb[m])
        rh = stats.spearmanr(LOGR[mh], 100 * (v.ma[mh] - v.mb[mh]) / v.nneg[mh])
        lencorr_rows.append(dict(set=s, grader=g, n_items=int(m.sum()), spearman_logratio_gain=r2(rg.statistic, 3), p_gain=fp(rg.pvalue),
                                 n_harm_items=int(mh.sum()), spearman_logratio_harm=r2(rh.statistic, 3), p_harm=fp(rh.pvalue),
                                 median_len_asha=int(np.floor(np.median(LEN_A[sm]) + 0.5)), median_len_bare=int(np.floor(np.median(LEN_B[sm]) + 0.5)),
                                 share_asha_longer_pct=r2(100 * (LEN_A[sm] > LEN_B[sm]).mean(), 1)))
dump("length_tertiles", len_rows)
dump("length_correlations", lencorr_rows)


# ----------------------------------------------------------------------------- (e) length-controlled gain

def ols_hc3(x, y):
    X = np.column_stack([np.ones_like(x), x])
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    e = y - X @ beta
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    meat = X.T @ (X * (e ** 2 / (1 - h) ** 2)[:, None])
    return beta, np.sqrt(np.diag(XtXi @ meat @ XtXi))


print("(e) length-controlled gain ...")
lc_rows = []
for g in GRADERS:
    for s in SETS:
        v = V[(g, PRIMARY)]
        m = v.mask & SETMASK[s]
        x, y = LOGR[m], v.sa[m] - v.sb[m]
        beta, se = ols_hc3(x, y)
        bi, bs = [], []
        for idx in chunks(rng_for("lc", g, s), len(x), B_CI):
            xx, yy = x[idx], y[idx]
            xm, ym = xx.mean(1, keepdims=True), yy.mean(1, keepdims=True)
            sl = ((xx - xm) * (yy - ym)).sum(1) / ((xx - xm) ** 2).sum(1)
            bs.append(sl)
            bi.append(ym[:, 0] - sl * xm[:, 0])
        bi, bs = np.concatenate(bi), np.concatenate(bs)
        w = np.abs(x) <= math.log(1.25)
        yw = y[w]
        wb = np.concatenate([yw[idx].mean(1) for idx in chunks(rng_for("lc25", g, s), len(yw), B_CI)])
        z = stats.norm.ppf(0.975)
        lc_rows.append(dict(grader=g, set=s, n=int(m.sum()), raw_gain=r2(y.mean()),
                            gain_at_equal_length=r2(beta[0]), ci_boot_lo=r2(pct(bi)[0]), ci_boot_hi=r2(pct(bi)[1]),
                            ci_hc3_lo=r2(beta[0] - z * se[0]), ci_hc3_hi=r2(beta[0] + z * se[0]),
                            slope_per_log_unit=r2(beta[1]), slope_ci_lo=r2(pct(bs)[0]), slope_ci_hi=r2(pct(bs)[1]),
                            share_of_raw_gain=r2(beta[0] / y.mean(), 3),
                            n_within_25pct=int(w.sum()), gain_within_25pct=r2(yw.mean()),
                            within25_ci_lo=r2(pct(wb)[0]), within25_ci_hi=r2(pct(wb)[1])))
        S[("lc", g, s)] = lc_rows[-1]
dump("length_controlled_gain", lc_rows)


# ----------------------------------------------------------------------------- (f) grader agreement

print("(f) grader agreement ...")
kap_rows = []
PAIRS = (("gpt_4_1", "gpt_5_4"), ("gpt_4_1", "claude_opus_4_8"), ("gpt_5_4", "claude_opus_4_8"))
for arm in (ARM_A, ARM_B):
    for g1, g2 in PAIRS:
        for scope in ("negative", "all"):
            x, y = [], []
            for k in IDS:
                c1, c2 = G[arm][g1][k], G[arm][g2][k]
                keep = ~(c1["failed"] | c2["failed"])
                if scope == "negative":
                    keep &= c1["pts"] < 0
                x.append(c1["met"][keep])
                y.append(c2["met"][keep])
            x, y = np.concatenate(x), np.concatenate(y)
            kp, po = kappa(x, y)
            kap_rows.append(dict(set="Standard", arm="asha" if arm == ARM_A else "bare", pair=f"{g1} vs {g2}", scope=scope,
                                 n_criteria=len(x), observed_agreement=r2(po, 3), cohen_kappa=r2(kp, 3)))
            S[("kappa", arm, g1, g2, scope)] = kp
dump("grader_kappa", kap_rows)

dir_rows = []
for s in SETS:
    m = COMMON & SETMASK[s]
    D = {g: np.sign((V[(g, PRIMARY)].sa - V[(g, PRIMARY)].sb)[m]) for g in GRADERS}
    R = {g: (V[(g, PRIMARY)].sa - V[(g, PRIMARY)].sb)[m] for g in GRADERS}
    all_pos = int(((D["gpt_4_1"] > 0) & (D["gpt_5_4"] > 0) & (D["claude_opus_4_8"] > 0)).sum())
    all_neg = int(((D["gpt_4_1"] < 0) & (D["gpt_5_4"] < 0) & (D["claude_opus_4_8"] < 0)).sum())
    n = int(m.sum())
    dir_rows.append(dict(set=s, pair="all three", n_items=n, same_nonzero_sign_pct=r2(100 * (all_pos + all_neg) / n, 1),
                         all_three_asha_better=all_pos, all_three_asha_worse=all_neg, opposite_sign_pct="", pearson_r=""))
    for g1, g2 in PAIRS:
        both = (D[g1] != 0) & (D[g2] != 0)
        dir_rows.append(dict(set=s, pair=f"{g1} vs {g2}", n_items=n,
                             same_nonzero_sign_pct=r2(100 * ((D[g1] == D[g2]) & both).sum() / n, 1),
                             all_three_asha_better="", all_three_asha_worse="",
                             opposite_sign_pct=r2(100 * ((D[g1] == -D[g2]) & both).sum() / n, 1),
                             pearson_r=r2(np.corrcoef(R[g1], R[g2])[0, 1], 3)))
dump("grader_direction_agreement", dir_rows)
for r in dir_rows:
    S[("dir", r["set"], r["pair"])] = r


# ----------------------------------------------------------------------------- (g) Hard vs non-Hard, headroom

print("(g) headroom ...")
hh_rows = []
for g in GRADERS:
    v = V[(g, PRIMARY)]
    grp = {"Hard": v.mask & IS_HARD, "non-Hard": v.mask & ~IS_HARD, "Standard": v.mask}
    pt, bt = {}, {}
    for name in ("Hard", "non-Hard"):
        a, b = v.sa[grp[name]], v.sb[grp[name]]
        d = a - b
        pt[name] = (d.mean(), b.mean(), d.mean() / (100 - b.mean()))
        gb, bb = [], []
        for idx in chunks(rng_for("hh", g, name), len(d), B_CI):
            gb.append(d[idx].mean(1))
            bb.append(b[idx].mean(1))
        bt[name] = (np.concatenate(gb), np.concatenate(bb))
    gdiff = bt["Hard"][0] - bt["non-Hard"][0]
    hdiff = bt["Hard"][0] / (100 - bt["Hard"][1]) - bt["non-Hard"][0] / (100 - bt["non-Hard"][1])
    std = S[("paired", g, "Standard", PRIMARY)]
    hh_rows.append(dict(grader=g, n_hard=int(grp["Hard"].sum()), n_nonhard=int(grp["non-Hard"].sum()),
                        gain_hard=r2(pt["Hard"][0]), gain_nonhard=r2(pt["non-Hard"][0]), gain_standard=r2(std["diff"]),
                        gain_hard_minus_nonhard=r2(pt["Hard"][0] - pt["non-Hard"][0]),
                        ci_lo=r2(pct(gdiff)[0]), ci_hi=r2(pct(gdiff)[1]),
                        bare_hard=r2(pt["Hard"][1]), bare_nonhard=r2(pt["non-Hard"][1]),
                        headroom_share_hard=r2(pt["Hard"][2], 3), headroom_share_nonhard=r2(pt["non-Hard"][2], 3),
                        headroom_share_diff=r2(pt["Hard"][2] - pt["non-Hard"][2], 3),
                        headroom_ci_lo=r2(pct(hdiff)[0], 3), headroom_ci_hi=r2(pct(hdiff)[1], 3)))
    S[("hh", g)] = hh_rows[-1]
dump("hard_vs_nonhard_headroom", hh_rows)


# ----------------------------------------------------------------------------- (h) small-sample tests

print("(h) psychosis, CL-bench, MedQA ...")
psy = [json.loads(l) for l in (BENCH / "psychosis-bench-2026-05-11/results/per_turn_judge_a.jsonl").open(encoding="utf-8")]
cnt = defaultdict(lambda: [0, 0])
for r in psy:
    if r["sis_eligible"]:
        c = cnt[(r["scenario_id"], r["arm"])]
        c[0] += int(r["sis"] == 1)
        c[1] += 1
scen = sorted({k[0] for k in cnt})
psy_rows = []
for sc in scen:
    a, b = cnt[(sc, "asha")], cnt[(sc, "gemini_flash")]
    psy_rows.append(dict(scenario_id=sc, asha_sis=a[0], asha_eligible=a[1], bare_sis=b[0], bare_eligible=b[1],
                         asha_rate=r2(a[0] / a[1], 3), bare_rate=r2(b[0] / b[1], 3),
                         direction="asha higher" if a[0] / a[1] > b[0] / b[1] else ("tie" if a[0] / a[1] == b[0] / b[1] else "bare higher")))
dump("psychosis_scenarios", psy_rows)
pa = np.array([r["asha_rate"] for r in psy_rows])
pb = np.array([r["bare_rate"] for r in psy_rows])
pw, pl = int((pa > pb).sum()), int((pa < pb).sum())
tot_a = sum(r["asha_sis"] for r in psy_rows), sum(r["asha_eligible"] for r in psy_rows)
tot_b = sum(r["bare_sis"] for r in psy_rows), sum(r["bare_eligible"] for r in psy_rows)
pboot = np.concatenate([(pa[idx] - pb[idx]).mean(1) for idx in chunks(rng_for("psy"), len(pa), B_CI)])


def mq(name):
    with (BENCH / f"medqa-2026-05-04/results/{name}_per_question.jsonl").open(encoding="utf-8") as fh:
        return {r["qid"]: r for r in map(json.loads, fh)}


qa, qg = mq("asha"), mq("gemini")
qids = sorted(qa)
b_raw = sum(qa[q]["correct"] and not qg[q]["correct"] for q in qids)
c_raw = sum(qg[q]["correct"] and not qa[q]["correct"] for q in qids)
both = [q for q in qids if qa[q]["parsed"] and qg[q]["parsed"]]
b_p = sum(qa[q]["correct"] and not qg[q]["correct"] for q in both)
c_p = sum(qg[q]["correct"] and not qa[q]["correct"] for q in both)
small = [
    dict(test="psychosis-bench May 2026, scenario-level exact sign test (SIS rate, judge A)", n_units=len(scen),
         asha_favoured=pw, comparator_favoured=pl, ties=len(scen) - pw - pl, p=fp(binom_p(pw, pw + pl)),
         estimate=f"mean scenario rate diff {100 * (pa - pb).mean():.1f} pp (scenario bootstrap 95% CI {100 * pct(pboot)[0]:.1f} to {100 * pct(pboot)[1]:.1f})",
         note="16 scenarios x 6 SIS-eligible turns; ties excluded"),
    dict(test="psychosis-bench May 2026, scenario-level Wilcoxon signed-rank", n_units=len(scen), asha_favoured=pw,
         comparator_favoured=pl, ties=len(scen) - pw - pl, p=fp(stats.wilcoxon(pa, pb, zero_method="wilcox").pvalue),
         estimate="", note="zero differences dropped"),
    dict(test="psychosis-bench May 2026, turn-level Fisher exact (reproduction)", n_units=tot_a[1] + tot_b[1],
         asha_favoured=tot_a[0], comparator_favoured=tot_b[0], ties="",
         p=fp(stats.fisher_exact([[tot_a[0], tot_a[1] - tot_a[0]], [tot_b[0], tot_b[1] - tot_b[0]]]).pvalue),
         estimate=f"{tot_a[0]}/{tot_a[1]} vs {tot_b[0]}/{tot_b[1]}", note="treats turns as independent"),
    dict(test="CL-bench biomedical 150, exact sign test on discordant items (bare 18 wins vs Asha 3)", n_units=150,
         asha_favoured=3, comparator_favoured=18, ties=129, p=fp(binom_p(3, 21)), estimate="7.3% vs 17.3% pass",
         note="counts from Docs/benchmarking/clbench/RESULTS.md via research/fig_data_lift_pairs.csv row K1; per-item data internal"),
    dict(test="MedQA 1,273, exact McNemar (format failures counted wrong)", n_units=len(qids), asha_favoured=b_raw,
         comparator_favoured=c_raw, ties=len(qids) - b_raw - c_raw, p=fp(binom_p(b_raw, b_raw + c_raw)),
         estimate=f"{sum(qa[q]['correct'] for q in qids)} vs {sum(qg[q]['correct'] for q in qids)} correct", note=""),
    dict(test="MedQA, both answers parsed, exact McNemar", n_units=len(both), asha_favoured=b_p, comparator_favoured=c_p,
         ties=len(both) - b_p - c_p, p=fp(binom_p(b_p, b_p + c_p)),
         estimate=f"{sum(qa[q]['correct'] for q in both)} vs {sum(qg[q]['correct'] for q in both)} correct", note="primary MedQA comparison"),
]
dump("small_sample_tests", small)
S["small"] = small


# ----------------------------------------------------------------------------- SUMMARY.md

def git_sha(p: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def md_table(rows: list[dict], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(out)


def pfloor(p: float, mult: int) -> str:
    floor = mult * 2 / (B_HARM + 1)
    return f"<= {floor:.0e}".replace("e-0", "e-") if p <= floor + 1e-12 else f"= {p:.2g}"


def f1(x, nd=1, sign=True):
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


hard_sha = hashlib.sha256(HARD_FILE.read_bytes()).hexdigest()[:16]
L = []
L.append("# Council analyses: numbers the manuscript may cite\n")
L.append("Generated by `_tools/council_analyses.py`; verified by `_tools/verify_council_analyses.py` "
         "(see `verification.csv`). Do not edit by hand; rerun the scripts.\n")
L.append("- Data: `EndlessRay/asha-benchmarks@" + git_sha(BENCH)[:12] + "`, the commit the paper cites; "
         f"Hard ids `{HARD_FILE.name}` sha256/16 `{hard_sha}` (1,000 ids).")
L.append(f"- Python {platform.python_version()}, NumPy {np.__version__}, SciPy {scipy.__version__}. Seed {SEED}; "
         f"B = {B_CI:,} item resamples for CIs, {B_HARM:,} for harm CIs and bootstrap P.")
L.append("- Points are percentage points of the HealthBench rubric score (item score x 100). Arms: Asha = `asha-apex-j-frozen`, bare = `bare-gpt-6-astra`.\n")

L.append("## Methods\n")
L.append("- **Item score**: `score` field = sum of points of met criteria / sum of positive points, unclipped (items can be negative). "
         "The verification script recomputes it from criteria.")
L.append("- **Failed grade**: a criterion whose explanation starts with `Parse failed` (no verdict) or `Backup parse` "
         "(verdict recovered by a fallback parser). Only Claude Opus 4.8 grades contain them.")
L.append("- **Pairing rule (primary, `readout`)**: an item is dropped from both arms for a grader if either arm's grade of that item "
         "contains a failed criterion. This is the rule the official readouts used; it reproduces their n and differences exactly. "
         "Sensitivity rules: `criterion` (keep all items, drop `Parse failed` criteria from both arms, rescore) and `all` "
         "(keep every stored verdict; the rule of `_tools/harm_ci.py`). GPT graders are unaffected by the rule.")
L.append("- **Bootstrap**: paired item-level percentile bootstrap (items resampled, both arms together). Bootstrap P two-sided, "
         "with +1 correction (floor 2/(B+1) = 1.0e-4 at B = 20,000).")
L.append("- **Harm estimators** (items with at least one negative criterion): criterion-pooled ratio (paper's), item-mean of per-item "
         "rates, item-level any-harm (share of items with at least one negative criterion met), severity-weighted (negative points met per item). "
         "Holm and Bonferroni across the six grader-by-set contrasts, within each estimator.")
L.append("- **Severe**: negative criterion with points <= -9. An item is Asha-only severe if Asha meets a severe criterion bare does not "
         "and bare meets none that Asha does not; unanimous = all three graders classify the item that way (items valid for all three). "
         "Exact two-sided binomial test on discordant items.")
L.append("- **Length**: characters of the final assistant message in `completions.jsonl.gz`; ratio = Asha / bare; tertiles cut on the log ratio "
         "within each set (grader-invariant). Length-controlled gain = intercept of OLS of per-item gain on log length ratio "
         "(gain at equal length), CI by item bootstrap, HC3 interval reported alongside.")
L.append("- **Agreement**: Cohen kappa on criterion `met`, pooled over items, criteria matched by position, failed grades excluded pairwise.\n")

L.append("## (a) Paired scores and the Opus pairing rule\n")
pr = [dict(Grader=PRETTY[r["grader"]], Set=r["set"], n=f"{r['n_paired']:,}", Asha=f"{r['asha_mean']:.2f}", Bare=f"{r['bare_mean']:.2f}",
           Diff=f"{r['diff']:+.2f}", CI=f"{r['ci_boot_lo']:+.2f} to {r['ci_boot_hi']:+.2f}", P_t=r["p_t"], WLT=f"{r['wins']}/{r['losses']}/{r['ties']}")
      for r in paired_rows if r["rule"] == PRIMARY]
L.append(md_table(pr, ["Grader", "Set", "n", "Asha", "Bare", "Diff", "CI", "P_t", "WLT"]))
L.append("")
for rr in recon_rows:
    L.append(f"- Opus {rr['set']}: failed-grade items Asha {rr['asha_items_failed_any']} (of which `Parse failed` {rr['asha_items_parse_failed']}), "
             f"bare {rr['bare_items_failed_any']} ({rr['bare_items_parse_failed']}), union {rr['union_failed_any']}. "
             f"Paired n = {rr['paired_n_readout_rule']:,}: Asha {rr['paired_asha_mean']:.2f}, bare {rr['paired_bare_mean']:.2f}, diff {rr['paired_diff']:+.2f}; "
             f"reproduces readout: {rr['reproduces_readout']}. The readout's Asha arm score {rr['readout_arm_score']:.2f} (n = {rr['readout_arm_n']:,}) "
             f"excludes only Asha's own failed items and is not a paired mean. All items, stored verdicts: n = {rr['n_all_items']:,}, "
             f"Asha {rr['asha_mean_all_items']:.2f}, bare {rr['bare_mean_all_items']:.2f}, diff {rr['diff_all_items']:+.2f}.")
for s in SETS:
    c = S[("paired", "claude_opus_4_8", s, "criterion")]
    L.append(f"- Opus {s}, `criterion` rule: n = {c['n_paired']:,}, diff {c['diff']:+.2f} ({c['ci_boot_lo']:+.2f} to {c['ci_boot_hi']:+.2f}).")
L.append("- Resolution: the readout (and Table 2, Figure 4) used the `readout` rule (n = 4,885 Standard, 963 Hard). The 4,932 is an Asha-only "
         "exclusion and must not be set beside the paired bare mean. The 4,996 figure in the Dennett review counts only `Parse failed` items; "
         "the readout also excluded `Backup parse` items, so the public files do reproduce the readout.\n")

L.append("## (b) Harm proxy under three estimators (primary pairing rule)\n")
hr = []
for g in GRADERS:
    for s in SETS:
        row = dict(Grader=PRETTY[g], Set=s)
        for e, lab in (("pooled", "Criterion-pooled"), ("item_mean", "Item-mean"), ("any_harm", "Item any-harm")):
            h = S[("harm", PRIMARY, e, g, s)]
            row[lab] = f"{h['diff']:+.2f} [{h['ci_lo']:+.2f}, {h['ci_hi']:+.2f}] P {pfloor(h['p_boot'], 1)}, Holm {pfloor(h['p_holm6'], 6)}"
        row["n"] = S[("harm", PRIMARY, "pooled", g, s)]["n_items"]
        hr.append(row)
L.append(md_table(hr, ["Grader", "Set", "n", "Criterion-pooled", "Item-mean", "Item any-harm"]))
L.append("")
L.append("Arm levels, criterion-pooled (%): " + "; ".join(
    f"{PRETTY[g]} {s} {S[('harm', PRIMARY, 'pooled', g, s)]['asha']:.2f} vs {S[('harm', PRIMARY, 'pooled', g, s)]['bare']:.2f}"
    for g in GRADERS for s in SETS) + ".")
L.append("Bonferroni-adjusted P (x6) is in `harm_estimators.csv` (`p_bonf6`). `<=1e-4` means no bootstrap replicate crossed zero "
         "(floor 2/(B+1)); the Holm value for such a contrast is then an upper bound. Holm on the official grader's Hard contrast: "
         "its raw P is the fourth smallest of six, so the multiplier is 3 (threshold 0.05/3 = 0.0167).")
L.append("Severity-weighted (negative points met per item, Asha minus bare): " + "; ".join(
    f"{PRETTY[g]} {s} {S[('harm', PRIMARY, 'severity', g, s)]['diff']:+.2f} [{S[('harm', PRIMARY, 'severity', g, s)]['ci_lo']:+.2f}, {S[('harm', PRIMARY, 'severity', g, s)]['ci_hi']:+.2f}]"
    for g in GRADERS for s in SETS) + ".")
L.append("Sensitivity: rule `all` reproduces `research/harm_ci.csv` estimators to the CSV's precision (see `verification.csv`); "
         "rule `criterion` moves no pooled estimate by more than " +
         f"{max(abs(S[('harm', 'criterion', 'pooled', g, s)]['diff'] - S[('harm', 'all', 'pooled', g, s)]['diff']) for g in GRADERS for s in SETS):.3f} points relative to `all`.\n")

L.append("## (c) Tails\n")
tr = [dict(Grader=PRETTY[r["grader"]], Set=r["set"], n=r["n"], Lost50=f"{r['items_lost_ge50']} ({r['share_lost_ge50_pct']:.1f}%)",
           Won50=f"{r['items_won_ge50']} ({r['share_won_ge50_pct']:.1f}%)", P=r["p_binom_lost_vs_won"],
           Worst5=f"{r['worst5pct_mean_asha']:.1f} vs {r['worst5pct_mean_bare']:.1f}") for r in tail_rows]
L.append(md_table(tr, ["Grader", "Set", "n", "Lost50", "Won50", "P", "Worst5"]))
L.append("\nLost50/Won50: items where Asha scored at least 50 points below / above bare. Worst5: mean of the worst 5% of item scores, Asha vs bare.\n")
sr = [dict(Set=r["set"], Grader=PRETTY.get(r["grader"], "Unanimous (all three)"), n=r["n_items"],
           Items=f"{r['items_asha_only']} vs {r['items_bare_only']}", P=r["p_binom_items"],
           Criteria=(f"{r['crit_asha_only']} vs {r['crit_bare_only']}" if r["crit_asha_only"] != "" else ""))
      for r in sev_rows if r["threshold"] == f"points<={SEVERE}"]
L.append(f"Severe criteria (points <= {SEVERE}), discordant items Asha-only vs bare-only:\n")
L.append(md_table(sr, ["Set", "Grader", "n", "Items", "P", "Criteria"]))
L.append("\nThresholds -7 and -10 are in `tails_severe_discordance.csv`. Criterion-level counts are clustered within items; use the item counts for inference.")
L.append("Unanimous swings: " + "; ".join(
    f"{r['set']} >= {r['threshold_points']} points {r['unanimous_asha_worse']} Asha-worse vs {r['unanimous_asha_better']} Asha-better (P = {r['p_binom']})"
    for r in swing_rows) + ".\n")

L.append("## (d) Harm and score gain by length-ratio tertile\n")
lr = [dict(Set=r["set"], Grader=PRETTY[r["grader"]], Tertile=r["tertile"], MedianRatio=r["ratio_median"],
           Gain=f"{r['score_gain']:+.1f} [{r['gain_ci_lo']:+.1f}, {r['gain_ci_hi']:+.1f}]",
           Harm=f"{r['harm_pooled_diff']:+.1f} [{r['harm_ci_lo']:+.1f}, {r['harm_ci_hi']:+.1f}]") for r in len_rows]
L.append(md_table(lr, ["Set", "Grader", "Tertile", "MedianRatio", "Gain", "Harm"]))
L.append("\nHarm is the criterion-pooled difference within the tertile. Spearman correlations are in `length_correlations.csv`: " + "; ".join(
    f"{PRETTY[r['grader']]} {r['set']} harm rho {r['spearman_logratio_harm']:+.3f} (P = {r['p_harm']})" for r in lencorr_rows if r["set"] == "Standard") + ".")
lcs = [r for r in lencorr_rows if r["grader"] == "gpt_4_1"]
L.append("Lengths: " + "; ".join(f"{r['set']} median {r['median_len_asha']:,} vs {r['median_len_bare']:,} characters, Asha longer on {r['share_asha_longer_pct']:.1f}% of items" for r in lcs) + ".\n")

L.append("## (e) Length-controlled gain (gain at equal length)\n")
lcr = [dict(Grader=PRETTY[r["grader"]], Set=r["set"], Raw=f"{r['raw_gain']:+.2f}",
            Intercept=f"{r['gain_at_equal_length']:+.2f} [{r['ci_boot_lo']:+.2f}, {r['ci_boot_hi']:+.2f}]",
            HC3=f"[{r['ci_hc3_lo']:+.2f}, {r['ci_hc3_hi']:+.2f}]", Slope=f"{r['slope_per_log_unit']:.1f}",
            Share=f"{r['share_of_raw_gain']:.2f}", Within25=f"{r['gain_within_25pct']:+.1f} (n = {r['n_within_25pct']})") for r in lc_rows]
L.append(md_table(lcr, ["Grader", "Set", "Raw", "Intercept", "HC3", "Slope", "Share", "Within25"]))
L.append("\nSlope: points of gain per unit of log(Asha length / bare length). Within25: mean gain on items whose two answers are within 25% of each other's length.\n")

L.append("## (f) Grader agreement\n")
kr = [dict(Arm=r["arm"], Pair=r["pair"], Scope=r["scope"], n=f"{r['n_criteria']:,}", Agreement=r["observed_agreement"], Kappa=r["cohen_kappa"]) for r in kap_rows]
L.append(md_table(kr, ["Arm", "Pair", "Scope", "n", "Agreement", "Kappa"]))
L.append("")
dr = [dict(Set=r["set"], Pair=r["pair"], n=r["n_items"], SameSign=r["same_nonzero_sign_pct"], Opposite=r["opposite_sign_pct"], r=r["pearson_r"]) for r in dir_rows]
L.append(md_table(dr, ["Set", "Pair", "n", "SameSign", "Opposite", "r"]))
L.append("\nSameSign: % of items where the graders give the same nonzero sign to Asha minus bare. r: Pearson correlation of per-item gains.\n")

L.append("## (g) Hard vs non-Hard and headroom\n")
hhr = [dict(Grader=PRETTY[r["grader"]], Hard=f"{r['gain_hard']:+.2f}", NonHard=f"{r['gain_nonhard']:+.2f}",
            Diff=f"{r['gain_hard_minus_nonhard']:+.2f} [{r['ci_lo']:+.2f}, {r['ci_hi']:+.2f}]",
            HeadroomHard=f"{r['headroom_share_hard']:.3f}", HeadroomNonHard=f"{r['headroom_share_nonhard']:.3f}",
            HeadroomDiff=f"{r['headroom_share_diff']:+.3f} [{r['headroom_ci_lo']:+.3f}, {r['headroom_ci_hi']:+.3f}]") for r in hh_rows]
L.append(md_table(hhr, ["Grader", "Hard", "NonHard", "Diff", "HeadroomHard", "HeadroomNonHard", "HeadroomDiff"]))
L.append("\nHeadroom share = gain / (100 - bare mean) within the group. Non-Hard = the 4,000 Standard items outside Hard (Opus: after the pairing rule).\n")

L.append("## (h) Small-sample tests\n")
L.append(md_table([dict(Test=r["test"], n=r["n_units"], For=r["asha_favoured"], Against=r["comparator_favoured"], Ties=r["ties"], P=r["p"], Estimate=r["estimate"]) for r in small],
                  ["Test", "n", "For", "Against", "Ties", "P", "Estimate"]))
L.append("\nFor = units favouring Asha; Against = units favouring the comparator. Psychosis per-scenario counts in `psychosis_scenarios.csv`.\n")

L.append("## Files\n")
for p in sorted(OUT.glob("*.csv")):
    L.append(f"- `{p.name}`")
(OUT / "SUMMARY.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("wrote", OUT)
