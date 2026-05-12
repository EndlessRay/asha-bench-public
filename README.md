# DNAi Public Benchmark Artifacts

Bit-exact reproducible artifacts for every public benchmarking claim DNAi makes about its medical AI agent **Asha** (live at [askasha.org](https://askasha.org)). Every input dataset is SHA-256 locked; every analysis script is self-contained; every overturned claim is documented in the same Git history.

## The arc — MedQA → META_CORRECT → Psychosis-bench

Three artifacts, one story.

### Chapter 1 — MedQA (2026-05-04)

→ [`medqa-2026-05-04/`](medqa-2026-05-04/)

Canonical Jin et al. 2020 USMLE 4-option test split (n = 1,273, dataset SHA-256 `c3b905cc…60a2beb`). 5-arm single-shot. **Asha 95.52%** (Wilson [94.24, 96.53]), statistically indistinguishable from Claude Opus 4.5 (paired McNemar p = 0.228) at roughly a quarter of Opus's marginal per-query cost. Architecturally important: **+3.22 pp paired McNemar lift over bare Gemini 3.1 Pro Preview** (p = 2.0×10⁻⁵, OR 2.64 [1.67, 4.18]).

One original claim ("Asha's wrong answers are independent of Gemini's") was overturned by an internal audit and is publicly retracted in [`medqa-2026-05-04/reports/03_wrong_letter_test.md`](medqa-2026-05-04/reports/03_wrong_letter_test.md). Audit also surfaced the mechanism: **51 of Gemini's 71 parse-failures became correct Asha letters via META_CORRECT, accounting for 51 of 66 paired wins** — the bridge to Chapter 2.

### Chapter 2 — META_CORRECT (the architectural primitive)

→ [`meta-correct/`](meta-correct/)

A deterministic, evidence-grounded, cryptographically-auditable post-emission corrector for structured LM outputs in regulated domains. US Provisional 397222-7002P1 (filed 2026-05-01); CIP draft on file with counsel. Patent spec held internally; this chapter documents the *empirical effect* by cross-referencing Chapter 1's parse-failure table with Chapter 3's safety-intervention table.

| Arm (on MedQA) | Parse-failure rate |
|---|---:|
| Asha (embodying META_CORRECT) | **0 / 1,273 = 0.00%** |
| GPT-4o | 0.00% • Claude Opus 4.5: 0.08% • o4-mini-high: 2.44% • Gemini 3.1 Pro: **5.58%** |

### Chapter 3 — Psychosis-bench (2026-05-11 / 12)

→ [`psychosis-bench-2026-05-11/`](psychosis-bench-2026-05-11/)

Au Yeung et al. (2025) 16-scenario × 12-turn protocol, [arXiv:2509.10970v2](https://arxiv.org/abs/2509.10970) **preprint**. 2-arm: Asha vs bare Gemini-2.5-Flash (the LM that powers Asha's verbalization layer on ~70% of routine queries). Same scenarios (SHA-256 locked), same judge (`gpt-4o-mini`), same eligibility windows. Pre-registration committed 11m 52s before bench start.

| Metric | Asha | Gemini-2.5-Flash | Effect |
|---|---:|---:|---|
| **DCS** (lower = safer, 0–2) | 0.354 | 1.215 | **3.43×** lower, scenario-paired bootstrap 95% CI [2.15, 6.13] |
| **HES** (lower = safer, 0–2) | 0.104 | 0.823 | **7.9×** lower |
| **SIS** rate (higher = safer, 0/1) | **92/96 = 95.8%** [0.898, 0.984] | **29/96 = 30.2%** [0.219, 0.400] | non-overlapping CIs (+65.6 pp gap) |

Two pre-registered hypotheses (H_DCS, H_SIS) PASS with wide margins. One (H_JUDGE_RELIABILITY) FAILS the κ ≥ 0.60 gate (avg κ_DCS+HES = 0.249); formal verdict therefore **INCONCLUSIVE per literal rule**. Substantive claim survives — both judges (`gpt-4o-mini` and `claude-haiku-4-5`) agree on the *direction* of every metric. Judge B is consistently harsher on Asha and more lenient on Gemini-Flash than Judge A (ordinal-scale calibration difference, not selective refusal); under Judge B alone the headline still shows Asha 1.72× lower DCS [1.40, 2.20] and 1.76× lower HES [1.37, 2.31]. Full breakdown: [`psychosis-bench-2026-05-11/reports/02_dual_judge_kappa.md`](psychosis-bench-2026-05-11/reports/02_dual_judge_kappa.md).

The same META_CORRECT layer responsible for MedQA's parser rescue is responsible for Psychosis-bench's intervention rate. MedQA failure mode is **structural** (does the LM produce a parseable letter?); Psychosis-bench failure mode is **semantic safety** (does the LM amplify a clinically dangerous belief?). One primitive, two regulated-domain failure modes.

## Layout

```
bench-public/
├── README.md                              this file
├── LICENSE                                Apache 2.0 (analysis scripts + computed reports)
├── medqa-2026-05-04/                      Chapter 1
├── meta-correct/                          Chapter 2 (public summary; spec held by counsel)
├── psychosis-bench-2026-05-11/            Chapter 3
└── PREREGISTRATION/                       commit-locked hypotheses
```

## Fiduciary contract

1. **Pre-registration.** Hypotheses and decision rules committed in Git *before* the run.
2. **Bit-exact reproducibility.** Every number reproduces from input SHA + per-turn / per-question JSONL + analysis script. No hidden post-processing.
3. **Honest disclosure.** Overturned claims, failed pre-reg gates, and methodological divergences from upstream are documented in the same Git history as the original. No silent corrections.
4. **Preprint discipline.** Upstream is named as preprint (Au Yeung 2025) or peer-reviewed (MedQA / Jin 2020). Never elided.

## Reproduce, end-to-end

```bash
git clone https://github.com/EndlessRay/asha-bench-public.git
cd asha-bench-public

# MedQA — download canonical dataset, verify SHA-256, recompute every reported number
python3 medqa-2026-05-04/scripts/verify_dataset_sha.py /path/to/jind11/MedQA/data/medqa_usmle_4opt_test.jsonl
python3 medqa-2026-05-04/scripts/compute_accuracy.py
python3 medqa-2026-05-04/scripts/mcnemar_paired_lift.py
python3 medqa-2026-05-04/scripts/wrong_letter_independence.py

# Psychosis-bench — verify scenario SHA-256, recompute every reported number
python3 psychosis-bench-2026-05-11/scripts/verify_scenarios_sha.py
python3 psychosis-bench-2026-05-11/scripts/compute_stats.py
```

## Contact

[founders@dnai.systems](mailto:founders@dnai.systems)
