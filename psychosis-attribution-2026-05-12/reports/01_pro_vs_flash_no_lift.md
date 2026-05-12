# Report 01 — Bare Gemini-2.5-Pro vs bare Gemini-2.5-Flash: no measurable tier lift

**Pre-registration**: `PREREGISTRATION/2026-05-12_BENCH6_GEMINI_PRO.md` (committed to internal Git at `1ace4b0a` before the run; mirrored here before public release).
**Run date**: 2026-05-12 (v2; v1 retracted — see `forensic/v1_truncation_bug/RETRACTED.md`).
**Judge**: `gpt-4o-mini`, temperature 0. Byte-identical DCS/HES prompts to upstream `psy_bench/core/scoring.py`. Broader SIS prompt (see Chapter 3 `reports/04_upstream_fidelity_audit.md`).

## Headline

| Arm | DCS mean | HES mean | SIS rate | SIS Wilson 95% CI |
|---|---:|---:|---:|---|
| Bare `gemini-2.5-pro` | 1.188 | 0.896 | 25/96 = **26.0%** | [0.183, 0.356] |
| Bare `gemini-2.5-flash` (Chapter 3 control) | 1.215 | 0.823 | 29/96 = **30.2%** | [0.219, 0.400] |
| Asha (Chapter 3 control) | **0.354** | **0.104** | 92/96 = **95.8%** | [0.898, 0.984] |

Scenario-paired bootstrap 95% CI on (Flash DCS / Pro DCS) ratio: **[0.86, 1.21]**, straddles 1.0.
Scenario-paired bootstrap 95% CI on (Pro DCS / Asha DCS) ratio: **[2.10, 6.17]**, well above 1.0.

## What this means

The Flash→Pro tier jump within the Gemini 2.5 family provides **no statistically significant safety lift** on adversarial multi-turn psychosis dialogues (H_PRO_OVER_FLASH FAIL, pre-registered decision rule). Both bare Gemini tiers confirm or amplify delusional beliefs at nearly identical rates (~1.19-1.22 DCS mean).

Asha towers over both: 3.35× lower DCS than bare Pro (bootstrap 95% CI [2.10, 6.17]), non-overlapping SIS CIs (Asha LB 0.898 > Pro UB 0.356).

## Hypothesis verdicts

| Hypothesis | Rule | Verdict |
|---|---|:---:|
| H_PRO_NOT_AT_CEILING | DCS-nonzero Wilson LB ≥ 0.50 OR SIS Wilson UB ≤ 0.85 | ✓ PASS |
| H_PRO_VS_ASHA | Bootstrap LB on (Pro DCS / Asha DCS) ≥ 1.5 OR Asha SIS LB > Pro SIS UB | ✓ PASS |
| H_PRO_OVER_FLASH | Bootstrap LB on (Flash DCS / Pro DCS) ≥ 1.2 | ✗ FAIL |

H_PRO_OVER_FLASH FAIL is the informative outcome — it closes the "better tier" confound.

## Raw data

- `results/per_turn_bench6_pro.jsonl` — 192 turns, 0 empty responses, 0 judge errors
- `results/aggregate_bench6.json` — full per-arm aggregates + Wilson CIs + bootstrap CIs + explicit hypothesis verdicts
