# NOTICE: Attribution

This repository contains analysis scripts and computed reports (Apache 2.0,
see `LICENSE`) plus *anonymized per-question / per-turn record exports* that
are downstream artifacts of public, third-party benchmark inputs.

## Upstream benchmarks (cite these in any derivative work)

1. **MedQA**: Jin, D., Pan, E., Oufattole, N., Weng, W.-H., Fang, H., &
   Szolovits, P. (2020). *What disease does this patient have? A large-scale
   open-domain question answering dataset from medical exams.* arXiv:2009.13081.
   Dataset SHA-256 locked in `medqa-2026-05-04/data/DATASET_LOCK.md`.

2. **Psychosis-bench**: Au Yeung, J., Dalmasso, J., Foschini, L.,
   Dobson, R. J. B., & Kraljevic, Z. (2025). *The Psychogenic Machine:
   Simulating AI Psychosis, Delusion Reinforcement and Harm Enablement in
   Large Language Models.* arXiv:2509.10970v2 **(preprint, not peer-reviewed)**.
   Scenarios SHA-256 locked in `psychosis-bench-2026-05-11/data/DATASET_LOCK.md`.

3. **HealthBench** (rubric protocol reused by the enclomiphene-bench clinician
   arm): Arora, R. K., et al. (2025). *HealthBench: Evaluating Large Language
   Models Towards Improved Human Health.* arXiv:2505.08775. The 18 clinician
   prompts and 116 rubric items in `enclomiphene-bench-2026-09-18/data/` are
   DNAi-authored and released under this repository's license; only the scoring
   protocol is HealthBench's.

## Models evaluated

The model arms compared in this repository (Asha by DNAi Systems, GPT-4o /
o4-mini-high by OpenAI, Claude Opus 4.5 by Anthropic, Gemini 3.1 Pro Preview
and gemini-2.5-flash by Google) were accessed through their official APIs
during the benchmark windows on 2026-05-04 (MedQA) and 2026-05-11 / 2026-05-12
(Psychosis-bench). Per-arm model snapshots, routing details, and any
deviations from upstream protocols are documented per chapter. The
enclomiphene-bench arms (Asha, `gemini-3.5-flash` via Vertex AI,
`claude-sonnet-4-5`, `gpt-5`) were accessed on 2026-09-18.

## Patent

The **META_CORRECT** architectural primitive referenced in Chapter 2 is
covered by US Provisional 397222-7002P1 (filed 2026-05-01); a continuation-in-part
draft is on file with counsel of record (Saul Ewing). The patent
specification is not part of this repository.

## Contact

[founders@dnai.systems](mailto:founders@dnai.systems)

## Directories imported in October 2026

These came from separate public repositories, imported with full history. The originals are archived read-only.

| Directory | Source repository | Terms |
|---|---|---|
| `healthbench-5000-2026-09-20/`, `register/`, `tools/`, `MODEL_CARDS.md`, `BENCHMARKS.md` | `EndlessRay/dnai-models` | no license file in the source; re-grade, recompute, quote and criticize with attribution to DNAi Systems |
| `healthbench-2026-06-26/` | `EndlessRay/asha-healthbench-2026-06-26` | same as above |
| `aom-chart-2026-08/` | `EndlessRay/asha-aom-chart-2026-08` | same as above; the chart and packet belong to their author, [dochobbs/aom-chart](https://github.com/dochobbs/aom-chart) |
| `a2a/asha/`, `a2a/polymath/`, `a2a/sage/`, `a2a/artha/`, `a2a/harley/`, `a2a/feng/` | `EndlessRay/<agent>-a2a` | MIT, see each `LICENSE` |

HealthBench conversations and rubrics inside the completion and grade files are OpenAI's ([openai/simple-evals](https://github.com/openai/simple-evals)); HealthBench Professional items are not redistributed, at OpenAI's request. The Vishwanath et al. 500-item sample and its scoring pipeline are the study authors' ([nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks)).
