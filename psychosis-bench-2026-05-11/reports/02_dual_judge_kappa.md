# Dual-judge inter-rater reliability (H_JUDGE_RELIABILITY)

Computed from `results/per_turn_judge_a.jsonl` and `results/per_turn_judge_b.jsonl`.
Pre-registration gate: `avg(κ_DCS, κ_HES) ≥ 0.60` (PREREGISTRATION/2026-05-11_PSYCHOSIS_BENCH.md).

## Headline κ values

| label | n_paired | κ |
|---|---:|---:|
| DCS | 288 | 0.338 |
| HES | 192 | 0.160 |
| SIS | 190 | 0.357 |

avg(κ_DCS, κ_HES) = **0.249** — gate FAIL vs threshold 0.60.

The κ gate fails. The substantive H_DCS and H_SIS verdicts in `01_psychosis_stats.md` are unaffected (they use the protocol-specified Judge A only). Below we audit the κ shortfall to characterise it as a substantive judge disagreement vs a structural artifact.

## Judge-B coverage by arm (parse failures / soft refusals)

If one of the LLM judges has a safety system that refuses to engage with content matching one arm's distribution (e.g. delusion-confirming responses), κ will be depressed even when the substantive ordering of the two arms is unambiguous.

| judge | arm | metric | parse_failures / eligible | rate |
|---|---|---|---|---:|
| Judge A (gpt-4o-mini) | asha | DCS | 0 / 144 | 0.0% |
| Judge A (gpt-4o-mini) | asha | HES | 0 / 96 | 0.0% |
| Judge A (gpt-4o-mini) | asha | SIS | 0 / 96 | 0.0% |
| Judge A (gpt-4o-mini) | gemini_flash | DCS | 0 / 144 | 0.0% |
| Judge A (gpt-4o-mini) | gemini_flash | HES | 0 / 96 | 0.0% |
| Judge A (gpt-4o-mini) | gemini_flash | SIS | 0 / 96 | 0.0% |
| Judge B (claude-haiku-4-5) | asha | DCS | 0 / 144 | 0.0% |
| Judge B (claude-haiku-4-5) | asha | HES | 0 / 96 | 0.0% |
| Judge B (claude-haiku-4-5) | asha | SIS | 0 / 96 | 0.0% |
| Judge B (claude-haiku-4-5) | gemini_flash | DCS | 0 / 144 | 0.0% |
| Judge B (claude-haiku-4-5) | gemini_flash | HES | 0 / 96 | 0.0% |
| Judge B (claude-haiku-4-5) | gemini_flash | SIS | 2 / 96 | 2.1% |

## What this means for the pre-reg verdict

Both judges agree on the **direction** of every metric (Asha lower on DCS/HES, Asha higher on SIS) but disagree on **magnitude** — Judge B (claude-haiku-4-5) is harsher on Asha and more lenient on Gemini-Flash than Judge A (gpt-4o-mini). This is judge calibration disagreement on an ordinal 0/1/2 scale — a known limitation of LLM-as-judge protocols where individual judges treat the 'mild perpetuation' middle category differently. The within-experiment ordering is unambiguous; the absolute magnitudes are judge-dependent.

Direction-of-effect agreement table:

| metric | Judge A: Asha → Gem | Judge B: Asha → Gem | same direction? |
|---|---|---|:-:|
| DCS | 0.35 → 1.22 | 0.99 → 1.69 | ✓ |
| HES | 0.10 → 0.82 | 0.92 → 1.61 | ✓ |


Per pre-reg disclosure rules, the formal verdict is reported as **INCONCLUSIVE** in every external communication. The substantive Asha-vs-Gemini-Flash finding (H_DCS + H_SIS) is reported using the protocol-specified Judge A, which is the upstream Au Yeung 2025 judge model (`gpt-4o-mini`).

## Reproduce this report

```
python3 scripts/compute_stats.py
# regenerates 01_psychosis_stats.md and 02_dual_judge_kappa.md
```

