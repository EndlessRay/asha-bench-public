# Chapter 4 — Architectural Attribution (2026-05-12)

→ Chapter 3 established Asha's safety advantage over bare Gemini-2.5-Flash on the Au Yeung 2025 psychosis-bench. Chapter 4 tests whether that advantage is attributable to **Asha's symbolic cognition stack** or to alternative explanations.

**Pre-registration**: [`PREREGISTRATION/2026-05-12_BENCH6_GEMINI_PRO.md`](PREREGISTRATION/2026-05-12_BENCH6_GEMINI_PRO.md) (committed to internal Git at `1ace4b0a` before the run, 2026-05-12; timestamp verifiable in Citadel repo history).

**Benchmark**: Au Yeung et al. (2025), [arXiv:2509.10970v2](https://arxiv.org/abs/2509.10970) — **preprint, not peer-reviewed**. Same 16 scenarios, same judge (`gpt-4o-mini`), same eligibility windows as Chapter 3. Scenario SHA-256 locked in [`data/DATASET_LOCK.md`](data/DATASET_LOCK.md).

## The attributable question

Asha gravity-routes to Gemini-2.5-Pro on ~30% of high-gravity queries. The most plausible reviewer objection to Chapter 3's attribution is:

> "You compared Asha to bare Gemini-2.5-Flash. But Asha uses Pro for hard queries. Maybe the lift is just the Flash→Pro tier jump, not the symbolic stack."

This chapter pre-registers and tests that hypothesis directly.

## Headline result

| Arm | DCS mean | HES mean | SIS rate | SIS Wilson 95% CI |
|---|---:|---:|---:|---|
| Bare `gemini-2.5-pro` (BENCH6) | 1.188 | 0.896 | 25/96 = **26.0%** | [0.183, 0.356] |
| Bare `gemini-2.5-flash` (Chapter 3 control) | 1.215 | 0.823 | 29/96 = **30.2%** | [0.219, 0.400] |
| **Asha** (Chapter 3 control) | **0.354** | **0.104** | 92/96 = **95.8%** | [0.898, 0.984] |

**Bare Pro and bare Flash are statistically indistinguishable on DCS** (Flash/Pro ratio bootstrap 95% CI [0.86, 1.21], straddles 1.0). The tier jump within the Gemini 2.5 family provides zero measurable safety lift on this protocol.

Asha's advantage over bare Pro: 3.35× lower DCS (bootstrap 95% CI [2.10, 6.17]). Non-overlapping SIS CIs (Asha LB 0.898 vs Pro UB 0.356).

## Pre-registered hypothesis verdicts

| Hypothesis | Verdict |
|---|:---:|
| H_PRO_NOT_AT_CEILING — bare Pro is not at safety ceiling | ✓ PASS |
| H_PRO_VS_ASHA — Asha's lift is not explained by tier-jump | ✓ PASS |
| H_PRO_OVER_FLASH — Flash→Pro tier jump gives safety lift | ✗ FAIL (informative) |

H_PRO_OVER_FLASH FAIL is the key finding: it closes the "better tier" confound.

## Artifact disclosure

A v1 run was retracted before any external publication. See [`forensic/v1_truncation_bug/RETRACTED.md`](forensic/v1_truncation_bug/RETRACTED.md) for the full disclosure. Root cause: `gemini-2.5-pro` is a thinking model; the v1 arm inherited a `max_output_tokens=1024` cap that was exhausted by hidden chain-of-thought tokens, producing 191/192 empty responses. Fixed before v2 was run.

## Combined attribution chain

See [`reports/02_combined_attribution_chain.md`](reports/02_combined_attribution_chain.md) for how BENCH3 (Chapter 3) + BENCH5 (Anthropic family) + BENCH6 (Gemini Pro tier) together close the principal alternative explanations for Asha's safety advantage.

## Layout

```
psychosis-attribution-2026-05-12/
├── README.md                        this file
├── PREREGISTRATION/
│   └── 2026-05-12_BENCH6_GEMINI_PRO.md
├── data/
│   └── DATASET_LOCK.md              same scenario SHA as Chapter 3
├── results/
│   ├── per_turn_bench6_pro.jsonl    192 turns, 0 empty, 0 errors
│   └── aggregate_bench6.json        Wilson CIs + bootstrap CIs + verdicts
├── forensic/
│   └── v1_truncation_bug/
│       ├── RETRACTED.md
│       ├── v1_per_turn.jsonl        artifact data (do not use)
│       └── v1_aggregate.json        artifact statistics (do not use)
└── reports/
    ├── 01_pro_vs_flash_no_lift.md
    └── 02_combined_attribution_chain.md
```

## Reproduce

```bash
# Verify scenario SHA (same as Chapter 3)
python3 psychosis-bench-2026-05-11/scripts/verify_scenarios_sha.py

# Recompute all statistics and verdicts from per_turn_bench6_pro.jsonl
python3 scripts/bench6_stats.py
```

## Citation

Au Yeung, J., Dalmasso, J., Foschini, L., Dobson, R. J. B., & Kraljevic, Z. (2025). *The Psychogenic Machine: Simulating AI Psychosis, Delusion Reinforcement and Harm Enablement in Large Language Models.* **arXiv:2509.10970v2 [preprint, not peer-reviewed]**.
