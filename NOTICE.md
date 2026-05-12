# NOTICE — Attribution

This repository contains analysis scripts and computed reports (Apache 2.0,
see `LICENSE`) plus *anonymized per-question / per-turn record exports* that
are downstream artifacts of public, third-party benchmark inputs.

## Upstream benchmarks (cite these in any derivative work)

1. **MedQA** — Jin, D., Pan, E., Oufattole, N., Weng, W.-H., Fang, H., &
   Szolovits, P. (2020). *What disease does this patient have? A large-scale
   open-domain question answering dataset from medical exams.* arXiv:2009.13081.
   Dataset SHA-256 locked in `medqa-2026-05-04/data/DATASET_LOCK.md`.

2. **Psychosis-bench** — Au Yeung, J., Dalmasso, J., Foschini, L.,
   Dobson, R. J. B., & Kraljevic, Z. (2025). *The Psychogenic Machine:
   Simulating AI Psychosis, Delusion Reinforcement and Harm Enablement in
   Large Language Models.* arXiv:2509.10970v2 **(preprint, not peer-reviewed)**.
   Scenarios SHA-256 locked in `psychosis-bench-2026-05-11/data/DATASET_LOCK.md`.

## Models evaluated

The model arms compared in this repository (Asha by DNAi Systems, GPT-4o /
o4-mini-high by OpenAI, Claude Opus 4.5 by Anthropic, Gemini 3.1 Pro Preview
and gemini-2.5-flash by Google) were accessed through their official APIs
during the benchmark windows on 2026-05-04 (MedQA) and 2026-05-11 / 2026-05-12
(Psychosis-bench). Per-arm model snapshots, routing details, and any
deviations from upstream protocols are documented per chapter.

## Patent

The **META_CORRECT** architectural primitive referenced in Chapter 2 is
covered by US Provisional 397222-7002P1 (filed 2026-05-01); a continuation-in-part
draft is on file with counsel of record (Saul Ewing). The patent
specification is not part of this repository.

## Contact

[founders@dnai.systems](mailto:founders@dnai.systems)
