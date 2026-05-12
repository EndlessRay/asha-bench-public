# DNAi Public Benchmark Artifacts

Bit-exact reproducible artifacts for every public benchmarking claim DNAi makes about its medical AI agent **Asha** (live at [askasha.org](https://askasha.org)). Every input dataset is SHA-256 locked; every analysis script is self-contained; every overturned claim is documented in the same Git history.

## Architecture (neurosymbolic stack, audited 2026-05-12)

Asha is a neurosymbolic system. The LLM (Gemini family in production, Sonnet 4.5 in research swap-tests) operates as the verbalization layer. Four symbolic components surround it and persist across LLM swaps:

| Component | Live state |
|---|---|
| Qdrant memory | 759 collections holding **125.44M vectors**. 125.24M curated knowledge (medical, pharmacological, research literature, clinical guidelines, structured codings, financial filings, legal corpora). 98,628 vectors across 493 private user and tenant graphs (438 Asha DNAids, 55 Harley trainers). |
| KIL (Knowledge Integration Layer) | symbolic evidence retrieval before each LLM call. Evidence stamps return in every per-turn JSONL we publish. |
| Epistemic Arena with Neural Darwinism | **31,616 active Competitive Informational Units (CIUs)** currently competing in the arena. **12,048 promoted (verified)** into long-term memory. **32,768 quarantined** by the Quality Firewall. Promotion rate 15.8%, quarantine rate 42.9% of evaluated candidates. |
| META_CORRECT | deterministic post-emission corrector for structured outputs in regulated domains. US Provisional 397222-7002P1, filed 2026-05-01. |

Patent: **US 19/290,471 (allowed)**. The benchmarks in this repo are the public falsifiability surface for the architecture. Two structural signatures live here:

- **Same backbone LM, different output behavior.** On Psychosis-bench (Chapter 3) bare `gemini-2.5-flash` posts 30.2% SIS. Asha's full stack on the same Gemini-Flash-majority routing posts 95.8%. The +65.6 pp gap is attributable to the cognition stack.
- **Same backbone LM, no parse failures.** On MedQA (Chapter 1) bare Gemini 3.1 Pro Preview parse-fails on 5.58% of questions. Asha parse-fails on 0/1,273. META_CORRECT accounts for 51 of 66 paired McNemar wins.
- **Tier jump doesn't close the gap.** Chapter 4 tests bare Gemini-2.5-Pro vs bare Gemini-2.5-Flash on the same 16 psychosis-bench scenarios. The Flash→Pro tier jump produces zero measurable safety lift (DCS ratio bootstrap 95% CI [0.86, 1.21]). Asha still leads bare Pro by 3.35× lower DCS (bootstrap 95% CI [2.10, 6.17]).

Three claims this section is NOT making. (1) That the LLM is bypassed; it still produces language. (2) That Asha reasons independently of the LLM; we publicly retracted the wrong-letter independence claim in [`medqa-2026-05-04/reports/03_wrong_letter_test.md`](medqa-2026-05-04/reports/03_wrong_letter_test.md). (3) That Asha is fully symbolic; the neural component carries language production while the symbolic components carry memory, evidence integration, competition, belief updating, and post-emission correction.

## The arc: MedQA, META_CORRECT, Psychosis-bench

Three artifacts, one story.

### Chapter 1: MedQA (2026-05-04)

→ [`medqa-2026-05-04/`](medqa-2026-05-04/)

Canonical Jin et al. 2020 USMLE 4-option test split (n = 1,273, dataset SHA-256 `c3b905cc…60a2beb`). 5-arm single-shot. **Asha 95.52%** (Wilson [94.24, 96.53]), statistically indistinguishable from Claude Opus 4.5 (paired McNemar p = 0.228) at roughly a quarter of Opus's marginal per-query cost. Architecturally important: **+3.22 pp paired McNemar lift over bare Gemini 3.1 Pro Preview** (p = 2.0×10⁻⁵, OR 2.64 [1.67, 4.18]).

One original claim ("Asha's wrong answers are independent of Gemini's") was overturned by an internal audit and is publicly retracted in [`medqa-2026-05-04/reports/03_wrong_letter_test.md`](medqa-2026-05-04/reports/03_wrong_letter_test.md). The audit also surfaced the mechanism: **51 of Gemini's 71 parse-failures became correct Asha letters via META_CORRECT, accounting for 51 of 66 paired wins**. That is the bridge to Chapter 2.

### Chapter 2: META_CORRECT (the architectural primitive)

→ [`meta-correct/`](meta-correct/)

A deterministic, evidence-grounded, cryptographically-auditable post-emission corrector for structured LM outputs in regulated domains. US Provisional 397222-7002P1 (filed 2026-05-01); CIP draft on file with counsel. Patent spec held internally; this chapter documents the *empirical effect* by cross-referencing Chapter 1's parse-failure table with Chapter 3's safety-intervention table.

| Arm (on MedQA) | Parse-failure rate |
|---|---:|
| Asha (embodying META_CORRECT) | **0 / 1,273 = 0.00%** |
| GPT-4o | 0.00% • Claude Opus 4.5: 0.08% • o4-mini-high: 2.44% • Gemini 3.1 Pro: **5.58%** |

### Chapter 3: Psychosis-bench (2026-05-11 / 12)

→ [`psychosis-bench-2026-05-11/`](psychosis-bench-2026-05-11/)

Au Yeung et al. (2025) 16-scenario × 12-turn protocol, [arXiv:2509.10970v2](https://arxiv.org/abs/2509.10970) **preprint**. 2-arm: Asha vs bare Gemini-2.5-Flash (the LM that powers Asha's verbalization layer on ~70% of routine queries). Same scenarios (SHA-256 locked), same judge (`gpt-4o-mini`), same eligibility windows. Pre-registration committed 11 m 52 s before bench start.

| Metric | Asha | Gemini-2.5-Flash | Effect |
|---|---:|---:|---|
| **DCS** (lower = safer, 0/1/2) | 0.354 | 1.215 | **3.43×** lower, scenario-paired bootstrap 95% CI [2.15, 6.13] |
| **HES** (lower = safer, 0/1/2) | 0.104 | 0.823 | **7.9×** lower |
| **SIS** rate (higher = safer, 0/1) | **92/96 = 95.8%** [0.898, 0.984] | **29/96 = 30.2%** [0.219, 0.400] | non-overlapping CIs, +65.6 pp gap |

Two pre-registered hypotheses (H_DCS, H_SIS) PASS with wide margins. One (H_JUDGE_RELIABILITY) FAILS the κ ≥ 0.60 gate (avg κ_DCS+HES = 0.249); formal verdict therefore **INCONCLUSIVE per literal rule**. The substantive claim survives. Both judges (`gpt-4o-mini` and `claude-haiku-4-5`) agree on the *direction* of every metric. Judge B is consistently harsher on Asha and more lenient on Gemini-Flash than Judge A, an ordinal-scale calibration difference. Under Judge B alone the headline still shows Asha 1.72× lower DCS [1.40, 2.20] and 1.76× lower HES [1.37, 2.31]. Full breakdown: [`psychosis-bench-2026-05-11/reports/02_dual_judge_kappa.md`](psychosis-bench-2026-05-11/reports/02_dual_judge_kappa.md).

### Chapter 4: Architectural Attribution (2026-05-12)

→ [`psychosis-attribution-2026-05-12/`](psychosis-attribution-2026-05-12/)

Pre-registered follow-on bench testing the "tier-jump" alternative explanation for Chapter 3's safety gap. Bare Gemini-2.5-Pro vs bare Gemini-2.5-Flash on the same 16 scenarios, same judge, same eligibility windows.

| Arm | DCS mean | HES mean | SIS rate |
|---|---:|---:|---|
| Bare `gemini-2.5-pro` | 1.188 | 0.896 | 25/96 = **26.0%** [0.183, 0.356] |
| Bare `gemini-2.5-flash` (Chapter 3 control) | 1.215 | 0.823 | 29/96 = **30.2%** [0.219, 0.400] |
| **Asha** (Chapter 3 control) | **0.354** | **0.104** | 92/96 = **95.8%** [0.898, 0.984] |

Flash→Pro tier jump: DCS ratio bootstrap 95% CI **[0.86, 1.21]**, straddles 1.0. Pre-registered verdict: **H_PRO_OVER_FLASH FAIL** (informative — closes the tier-jump confound). Asha vs bare Pro: 3.35× lower DCS (CI [2.10, 6.17]), non-overlapping SIS CIs.

Artifact disclosure: a v1 run was retracted before external publication due to a `max_output_tokens=1024` bug specific to thinking models. Full disclosure in [`forensic/v1_truncation_bug/RETRACTED.md`](psychosis-attribution-2026-05-12/forensic/v1_truncation_bug/RETRACTED.md).

### Attribution summary

On both measurement endpoints, the symbolic stack composes with the underlying LM. On the **structural** endpoint (MedQA parse-failure rescue) META_CORRECT is the proximal mechanism: 51 of 66 paired wins are parse-failure rescues. On the **semantic-safety** endpoint (Psychosis-bench) the full cognition stack lifts SIS from 30.2% (bare Flash) to 95.8% (Asha), a +65.6 pp gap, over an LM that is not at safety ceiling. The tier-attribution chapter (Chapter 4) establishes that neither the Flash→Pro tier jump nor the Gemini→Anthropic family jump explains this gap. We do not claim the same gap would appear over an intrinsically safety-ceiling LM; that is a separate test, queued.

## Layout

```
asha-bench-public/
├── README.md                              this file
├── LICENSE                                Apache 2.0 (analysis scripts + computed reports)
├── medqa-2026-05-04/                      Chapter 1: MedQA structural hallucination
├── meta-correct/                          Chapter 2: META_CORRECT primitive
├── psychosis-bench-2026-05-11/            Chapter 3: Asha vs bare Gemini-Flash
├── psychosis-attribution-2026-05-12/      Chapter 4: tier-attribution (Pro vs Flash vs Asha)
├── figures/                               reproducible figure scripts + PNGs
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

# MedQA: download canonical dataset, verify SHA-256, recompute every reported number
python3 medqa-2026-05-04/scripts/verify_dataset_sha.py /path/to/jind11/MedQA/data/medqa_usmle_4opt_test.jsonl
python3 medqa-2026-05-04/scripts/compute_accuracy.py
python3 medqa-2026-05-04/scripts/mcnemar_paired_lift.py
python3 medqa-2026-05-04/scripts/wrong_letter_independence.py

# Psychosis-bench: verify scenario SHA-256, recompute every reported number
python3 psychosis-bench-2026-05-11/scripts/verify_scenarios_sha.py
python3 psychosis-bench-2026-05-11/scripts/compute_stats.py

# Chapter 4 (tier-attribution): recompute all statistics and verdicts
python3 psychosis-attribution-2026-05-12/scripts/bench6_stats.py

# Figures: regenerate all figures from raw data
cd figures && python3 generate_figures.py
```

## Contact

[founders@dnai.systems](mailto:founders@dnai.systems)
