# Asha benchmarks

Per-item, re-gradable benchmark artifacts for **Asha**, the medical AI agent built by DNAi Systems ([askasha.org](https://askasha.org)).

Live register: [dnai.systems/benchmarks](https://dnai.systems/benchmarks) | JSON: [dnai.systems/benchmarks.json](https://dnai.systems/benchmarks.json) | API: `GET https://api.askasha.org/api/benchmarks`

Asha is an architecture that runs around a language model: retrieval from a curated medical corpus, specialist agents, claim falsification, and safety gates before and after generation. No model is fine-tuned. The test of the architecture is a paired one: run the same model alone and inside Asha, on the same items, under the same grader, and report the difference. Every comparison below is built that way, and every number links to data you can re-grade.

## Result: the same model scores higher inside Asha

| Benchmark | n | Grader | Model alone | Inside Asha | Difference (points) |
|---|---:|---|---|---|---|
| HealthBench Hard | 1,000 | gpt-4.1 (official) | GPT-6 Astra **29.4** | Apex-J **42.0** | **+12.6** [10.7, 14.4]; length-adjusted +9.9 [8.1, 11.8] |
| HealthBench, all conversations | 5,000 | gpt-4.1 (official) | GPT-6 Astra **52.7** | Apex-J **60.7** | **+8.0** [7.3, 8.7]; length-adjusted +5.6 [4.9, 6.3] |
| HealthBench, Vishwanath et al. 500 | 500 | the study's three-judge panel | GPT-6 Astra **54.9** | Apex-J **63.8** | **+8.9**; gpt-4.1 on the same 500: +8.4 [6.1, 10.7] |
| HealthBench Professional, holdout | 225 | GPT-5.4, length-adjusted | GPT-6 Astra **65.7** | Apex-J **67.9** | +2.2, p = 0.23, not significant; Claude Opus 4.8 grader: +4.6, p = 0.03 |
| HealthBench Professional | 524 | length-adjusted | Claude Sonnet 5 | Base | +0.3, p = 0.88, not significant; 191 red-team items: +10.1 |
| MedQA (USMLE, 4 options) | 1,273 | exact match | Gemini 3.1 Pro **92.3%** | Base **95.5%** | **+3.2**, McNemar p = 2.0e-5 |
| psychosis-bench, safe interventions | 96 turns | gpt-4o-mini (protocol judge) | Gemini 2.5 Flash **30.2%** | Base **95.8%** | **+65.6**, Fisher exact p = 4.0e-23 |

Brackets are 95% confidence intervals of the paired difference. Asha's estimate is higher in six of the seven comparisons and five are statistically significant. The seventh, Asha Base against Claude Sonnet 5 on all 524 Professional items, is a tie. HealthBench scores are on a 0 to 100 scale.

### What "inside Asha" means

| Configuration | Where it runs | What it adds to the model |
|---|---|---|
| **Base** | Most traffic; the API default | One retrieval-grounded pass with safety gates. A router sends harder questions to the larger model of the same family: Gemini 3.1 Pro or 3 Flash on MedQA; Gemini 2.5 Flash on about 70% of psychosis-bench turns and 2.5 Pro on the rest; Claude Sonnet 5 or Opus 5 on HealthBench Professional |
| **Apex-J** (frozen 20 September 2026) | High-stakes traffic | Eleven specialist agents, each with its own retrieval, running on Claude Sonnet 5 and Opus 5; FENG falsifies extracted claims against the corpus; GPT-6 Astra writes the final answer |

The Apex-J rows hold the answer-writing model fixed. The Asha arm also runs Claude models inside its agents, so those rows measure the whole system against its composer model alone. The Base rows are closer to a single-model test; on psychosis-bench, a separate attribution study shows that bare Gemini 2.5 Pro is no safer than bare 2.5 Flash, so the Pro share does not explain the gap ([`psychosis-attribution-2026-05-12/`](psychosis-attribution-2026-05-12/)).

## Safety

- **psychosis-bench** (Au Yeung et al. 2025; 16 scripted 12-turn scenarios): with the same model family, safe interventions rose from 30.2% to 95.8%, delusion confirmation fell 3.4-fold (scenario-paired bootstrap 95% CI 2.15 to 6.13) and harm enablement 7.9-fold. Both pre-registered effect hypotheses passed; agreement between the two judges fell below the pre-registered gate (kappa 0.25), which the pre-registration records as a formally inconclusive verdict. [`psychosis-bench-2026-05-11/`](psychosis-bench-2026-05-11/)
- **Red-team clinician prompts** (HealthBench Professional, 191 items): Asha Base on Claude Sonnet 5 scored +10.1 above Sonnet 5 alone.
- **Enclomiphene-bench, clinician arm** (18 adversarial prompts, DNAi-authored, small n): Asha triggered 0 of 29 harm criteria; bare Gemini 3.5 Flash, GPT-5 and Claude Sonnet 4.5 triggered them on 5, 6 and 3 prompts, and all three wrote an adolescent dose that Asha declined. These are different models from Asha's, so this is a system comparison. [`enclomiphene-bench-2026-09-18/`](enclomiphene-bench-2026-09-18/)
- **Identity invariance** (a clinician's locked pediatric chart): the plan, dose and duration stayed the same across 36 of 36 identity variants (insurance, race, name, caregiver age, occupation, interpreter). [`aom-chart-2026-08/`](aom-chart-2026-08/)
- **HealthBench harm proxy** (share of negative-point rubric criteria triggered, pre-registered bound: within +2.0 points of the bare model): on all 5,000 conversations the bound was **missed** under the official grader (+2.8) and met under GPT-5.4 (-0.3) and Claude Opus 4.8 (-0.4). The excess is concentrated in length and over-detail criteria; factual-error criteria account for 59 of the 1,851 extra hits. [`healthbench-5000-2026-09-20/readouts/`](healthbench-5000-2026-09-20/readouts/)

## Limits

1. **Length.** Asha's answers are about twice as long as the bare model's (median 2,725 against 1,400 characters). HealthBench rewards completeness, so the length-adjusted differences are reported next to the official ones; they are smaller and still significant.
2. **Composer held fixed.** The Apex-J comparisons hold the answer-writing model fixed while Asha's agents run other models (see above).
3. **Holdout.** On HealthBench Professional the shipped configuration was selected on a 300-item slice; on the 225 items never used for selection its lead under the ladder's official grader is +2.2 (p = 0.23).
4. **Strong models alone.** Today's frontier models alone also intervene safely on psychosis-bench (bare Claude Sonnet 4.5: 100%; bare Gemini 3.6 Flash: 93.8%). The 30.2% to 95.8% gap is what Asha added to a May 2026 model that was not at the safety ceiling.
5. **Web search.** In the Vishwanath et al. study, frontier models run with web search scored above every system here (GPT-5.2 88.0, Gemini 3.1 Pro 79.3, Claude Opus 4.6 77.0). Asha answers from its own corpus without web search; its like-for-like comparisons on that sample are with the study's clinical tools (OpenEvidence 62.6, UpToDate Expert AI 61.3, as published) and with its composer model under the same panel.
6. **Graders.** All rubric scores come from LLM graders. No blinded physician rating of these answers has been published yet.
7. **Validation.** The external re-runs and recomputations by Airpixels Innovations LLP were contracted by DNAi.
8. **Withheld data.** HealthBench Professional per-item data are withheld at OpenAI's request; those rows are aggregate only.
9. **Pretraining exposure.** MedQA and HealthBench are public, and every model may have seen them in pretraining. The paired difference controls for that; the absolute scores do not.

## Contamination

HealthBench answer keys, grading rubrics and stored model answers to benchmark items have been excluded from Asha's retrieval layer since 2 June 2026. Asha's own query log and unpromoted memory were removed from retrieval on 16 September 2026, after a probe found 17 of the 525 Professional prompts in the query log from a June run; every Apex-J row was measured after that change, and the Base-on-Sonnet-5 Professional row a few hours before it. A nearest-neighbour probe of 200 of the 5,000 HealthBench items found no retrievable benchmark content (cosine below 0.92 throughout). The MedQA run excluded DNAi's internal MedQA collection on every request (audit signature on 1,273 of 1,273 records); an n-gram sweep of the other collections for MedQA-derived text has not been run.

## Contents

| Path | What | Run date | Per-item data |
|---|---|---|---|
| [`healthbench-5000-2026-09-20/`](healthbench-5000-2026-09-20/) | Frozen Apex-J and bare GPT-6 Astra on all 5,000 HealthBench conversations under three graders; the Vishwanath 500 under the study's panel; identity and style checks; SHA-256 manifest | 2026-09-20 to 24 | yes |
| [`healthbench-2026-06-26/`](healthbench-2026-06-26/) | June 2026 HealthBench runs (Standard, Hard, Professional aggregates), pipeline glossary ([`PIPELINES.md`](healthbench-2026-06-26/PIPELINES.md)), preprint, audit receipt | 2026-06-26 | yes (Professional: aggregates) |
| [`medqa-2026-05-04/`](medqa-2026-05-04/) | Five arms on the SHA-256 locked MedQA test split, same day | 2026-05-04 | yes |
| [`meta-correct/`](meta-correct/) | The format-correction step behind the MedQA parse-failure result | 2026-05 | n/a |
| [`psychosis-bench-2026-05-11/`](psychosis-bench-2026-05-11/) | Asha against bare Gemini 2.5 Flash; two judges; pre-registered | 2026-05-11 | yes |
| [`psychosis-attribution-2026-05-12/`](psychosis-attribution-2026-05-12/) | Bare Gemini 2.5 Pro against 2.5 Flash: the tier jump adds no safety | 2026-05-12 | yes |
| [`enclomiphene-bench-2026-09-18/`](enclomiphene-bench-2026-09-18/) | DNAi-authored safety set, patient and clinician arms, four systems, two judges | 2026-09-18 | yes |
| [`aom-chart-2026-08/`](aom-chart-2026-08/) | Verbatim traces on a clinician's locked pediatric chart, identity variants | 2026-08-26 | yes |
| [`PREREGISTRATION/`](PREREGISTRATION/) | Commit-locked hypotheses | 2026-05-11 | n/a |
| [`MODEL_CARDS.md`](MODEL_CARDS.md) | The Asha tiers: architecture, models, intended use, limitations | 2026-09-24 | n/a |
| [`BENCHMARKS.md`](BENCHMARKS.md), [`register/`](register/), [`tools/`](tools/) | The register rendered as a document, its dated JSON, and the renderer | 2026-09-24 | n/a |
| [`a2a/`](a2a/) | Agent cards and integration guides (A2A protocol) for Asha, Polymath, Sage, Artha, Harley and FENG | | n/a |
| [`CHAPTERS.md`](CHAPTERS.md) | The May to September 2026 narrative of the MedQA, META_CORRECT, psychosis-bench, attribution and enclomiphene chapters, as first published | | n/a |
| [`figures/`](figures/) | Figure scripts and outputs | | n/a |

## Reproduce

```bash
git clone https://github.com/EndlessRay/asha-benchmarks && cd asha-benchmarks
bash reproduce.sh                                # MedQA, psychosis-bench, attribution: verify SHA-256 locks, recompute every statistic
python3 healthbench-2026-06-26/verify_audit.py   # June HealthBench audit receipt
```

For the 5,000-item run, `healthbench-5000-2026-09-20/` holds every completion and every per-criterion grade for both arms and all three graders, with SHA-256 in `MANIFEST.json`. Re-grade the completions with the official HealthBench grader ([openai/simple-evals](https://github.com/openai/simple-evals)) and compare with `readouts/`. The Vishwanath 500 panel grades re-run in the study's own pipeline, [nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks).

## History of this repository

This repository consolidates nine earlier public repositories, imported with their full commit history: `asha-bench-public` (renamed to this repository), `dnai-models`, `asha-healthbench-2026-06-26`, `asha-aom-chart-2026-08`, `asha-a2a`, `polymath-a2a`, `sage-a2a`, `artha-a2a`, `harley-a2a` and `feng-a2a`. The originals are archived read-only, so every published link to them still resolves.

## References

- HealthBench: Arora R. K. et al. *HealthBench: Evaluating Large Language Models Towards Improved Human Health.* arXiv:2505.08775 (2025).
- Vishwanath et al. *General-purpose large language models outperform specialized clinical AI tools on medical benchmarks.* Nature Medicine (2026). [doi:10.1038/s41591-026-04431-5](https://doi.org/10.1038/s41591-026-04431-5)
- MedQA: Jin D. et al. arXiv:2009.13081 (2020).
- psychosis-bench: Au Yeung J. et al. *The Psychogenic Machine.* arXiv:2509.10970v2 (2025, preprint).
- DNAi preprint: Singh D., Anand P. *An auditable, retrieval-grounded agent architecture improves medical accuracy and conversational safety in language models.* Research Square (2026). [doi:10.21203/rs.3.rs-10206806/v1](https://doi.org/10.21203/rs.3.rs-10206806/v1)
- Architecture: US Patent 12,555,008 B1.

## Licenses and use

Analysis code and reports from the original `asha-bench-public` are Apache-2.0 ([`LICENSE`](LICENSE)); each `a2a/` subdirectory carries its own MIT license. The imported benchmark directories came from repositories without a license file and keep their published terms: re-grade, recompute, quote and criticize them with attribution to DNAi Systems and a link to this repository. Upstream datasets and their citations are listed in [`NOTICE.md`](NOTICE.md). Citation metadata: [`CITATION.cff`](CITATION.cff).

Contact: open an issue in this repository.
