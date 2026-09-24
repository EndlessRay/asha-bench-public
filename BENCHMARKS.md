# DNAi benchmarks (public register)

Rendered from `benchmarks/register/benchmarks_live_2026-09-24.json` (register updated 2026-09-24). Canonical live page: https://dnai.systems/benchmarks. Canonical JSON: https://dnai.systems/benchmarks.json.

## Publication policy

A row is published only when it states its pipeline, its benchmark set with n, its grader, and an artifact. Every proportion carries a 95% interval. Comparators are labeled by how they were scored: same grader in our run, independent validator, vendor self-reported, or as published; only same-grader values share a bar with ours. Samples under n=100 sit in the appendix with their interval unless the benchmark's own protocol fixes n.

| Tier | Meaning |
|---|---|
| A | Public per-item artifact and public harness. Anyone can re-grade every item. |
| B | Public aggregate artifact (per-item data withheld by a third-party condition, or reported in a public preprint). Anyone can check the aggregate and the method. |
| C | Internal artifact, public release pending. Reported for completeness; weight it accordingly. |

| Comparator basis | Meaning |
|---|---|
| `same_grader_self_run` | The comparator model was run by us, in the same harness, scored by the same grader. |
| `independent_validator` | Run by the independent validator (Airpixels Innovations LLP) on the same protocol. |
| `vendor_reported` | Reported by the vendor on its own run. Same grader family at best; never the same run. |
| `literature` | Taken from a paper or the benchmark author. Different run, possibly a different item set. |

Production routes each query by clinical stakes to one of three tiers: Asha Base (P2, one retrieval-grounded pass), Asha Mid (P5, three-model merge), Asha Apex (P6, multi-expert ensemble with a domain-specialist composer). Every row names the tier that was measured. Base carries most routine traffic; Apex carries high-stakes traffic.

## Board

| Benchmark | Set | n | Configuration | Result | Grader | Best same-grader comparator | Tier |
|---|---|---|---|---|---|---|---|
| HealthBench Hard | Hard subset, full set | 1000 | Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on) | **42.0** [40.1, 43.7] | gpt-4.1 (the official HealthBench grader) | 40.3 GPT-5.2 (bare, retrieval off) | C |
| HealthBench Professional | Professional, full set, September 2026 board; every arm through one harness and one grader set | 525 | Asha Apex-J, Claude Fable 5.1 composer @4096 (best Asha configuration measured; two trials) | **65.1** | Claude Opus 4.8 (every arm on the board also graded by GPT-5.4 low and gpt-4.1) | 67.0 GPT-6 Astra (bare, xhigh), length-adjusted, two trials | C |
| HealthBench, 500-item sample (Vishwanath et al. harness) | Independent study's 500-item sample | 500 | Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on), graded in the study's public pipeline | **63.8** | three-judge panel, majority per criterion (anthropic-claude-4-6-opus, google-gemini-3-1-pro-preview, openai-gpt-5-2): the published study's configuration, run in its own pipeline | 54.9 GPT-6 Astra (bare, retrieval off) | B |
| MedQA USMLE, 4-option test split | Canonical test split, SHA-256 locked, single shot, same day across arms | 1273 | Deployed single-call engine | **95.5** [94.2, 96.5] | None (deterministic letter match, strict regex) | 94.7 Claude Opus 4.5 | A |
| psychosis-bench (Au Yeung et al. 2025) | Full protocol; 96 intervention-eligible turns per arm | 96 | Deployed engine, backbone gemini-2.5-flash | **95.8** [89.8, 98.4] | gpt-4o-mini (the benchmark's protocol judge); Claude Haiku 4.5 as second judge | 80.2 Bare GLM-5.2 (open weights) | A |
| Enclomiphene-bench v1.0, patient arm (psychosis-bench protocol) | Full protocol; 36 intervention-eligible turns per arm | 36 | Deployed engine, anthropic_routed backbone (claude-sonnet-4-6 / claude-opus-4-8 by gravity) | **100.0** [90.4, 100.0] | gpt-4o-mini (the psychosis-bench protocol judge); Claude Haiku 4.5 as second judge, same 36/36 | 100.0 Bare Claude Sonnet 4.5 | A |
| Locked pediatric AOM chart (Hobbs, dochobbs/aom-chart packet v5) | Locked 24-month stem | 14 | Deployed production build, serial runs, 2026-08-26 | **100.0** [78.5, 100.0] | Rubric applied by us to verbatim traces; the benchmark author's adjudication is pending and owns the scoreboard | none | A |
| HealthBench standard | Standard, full set | 5000 | Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on) | **60.7** [59.8, 61.5] | gpt-4.1 (the official HealthBench grader) | 52.7 GPT-6 Astra (bare, retrieval off) | C |
| KaBLE, belief-reasoning subset | 220-question subset spanning first-person, third-person, and recursive belief | 220 | Deployed single-call engine | **97.7** [94.8, 99.0] | None (answer-key match) | none | C |

## Rows

### HealthBench Hard: Hard subset, full set (`healthbench-hard-apex`)

- Pipeline / configuration: Apex-J; Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on)
- Deployed tier: Apex tier of the production cascade (APEX_TIER_PIPELINE=apex_j)
- Result: **42.0** [40.1, 43.7] (Rubric score; CI method bootstrap); n = 1000; run date 2026-09-21
- Grader: gpt-4.1 (the official HealthBench grader)
- Pre-registered harm test: pre-registered (CEILING_5000_GATE.md, A3): harm proxy vs bare Astra within +2.0 points on the 5,000: +1.6 points, bound 2.0, passed
- Comparators:
  - GPT-6 Astra (bare, retrieval off): 29.4 (n=1000), basis `same_grader_self_run`: same harness, same items, same grader; the composer backbone of Apex-J without the Asha layer; run 19 Sep 2026
  - Asha Apex (P6, June 2026 build): 44.8 (n=1000), basis `same_grader_self_run`: June 2026 run in the same harness (lineage; replaced by Apex-J on 20 Sep 2026); the same June answers re-graded by today's gpt-4.1 score 44.8 (n=1000)
  - GPT-5.2 (bare, retrieval off): 40.3 (n=798), basis `same_grader_self_run`: self-run June 2026 in the same harness, retrieval off; per-item JSONL not retained (aggregate only)
  - Gemini 3.1 Pro (bare, retrieval off): 20.6 (n=800), basis `same_grader_self_run`: self-run June 2026 in the same harness, retrieval off; per-item JSONL not retained (aggregate only)
  - GLM-5.2 (bare, open weights): 16.2 (n=1000), basis `same_grader_self_run`: self-run June 2026, full set, per-item JSONL in the public repo
  - Claude Opus 4.5 (bare, retrieval off): 11.6 (n=795), basis `same_grader_self_run`: self-run June 2026 in the same harness, retrieval off; per-item JSONL not retained (aggregate only)
  - Asha Mid (P5, three-model merge): 37.9 (n=898), basis `same_grader_self_run`
  - Asha Base (P2, single retrieval-grounded pass): 28.4 (n=1000), basis `same_grader_self_run`
- Paired statistics:
  - Apex-J vs bare GPT-6 Astra, same 1,000 items: +12.6 pp, W/L/T 604 / 222 / 174, n=1000, paired t-test, two-sided; exact sign test p = 1.4e-41, p=3.7e-37
  - Grader stability: today's gpt-4.1 vs June gpt-4.1 on the identical June P6 Hard completions: +0.0 pp, n=1000, same completions, mean clipped per-example score, p=n/a
  - Apex (P6) vs Mid (P5): +6.6 pp, W/L/T 449 / 309 / 140, n=898, two-sided sign test, p=4.1e-7
  - Mid (P5) vs Base (P2): +9.7 pp, W/L/T 497 / 250 / 151, n=898, two-sided sign test, p=1.0e-19
- Also measured:
  - Apex-J, GPT-5.4 grader (Hard 1,000): 37.3 vs 24.9 bare (n=1000). Sensitivity grader; official HealthBench grading is gpt-4.1. Harm proxy 25.9%. Paired vs bare Astra +12.4 pp.
- Notes: The served configuration (frozen Apex-J) on the full Hard 1,000, restricted from the same 5,000-item run (Hard is an exact subset of Standard), graded by gpt-4.1. Harm proxy 34.0%, 0 empty answers. Bare GPT-6 Astra is the composer backbone without the Asha layer on the same items, retrieval off. June 2026 bare frontier baselines and the June P6 build stay as lineage under the same grader; the June-vs-today grader-stability entry says how much of any P6-to-Apex-J difference is the grader. Scores independently recomputed from the June graded artifacts by Airpixels Innovations LLP (September 2026): Apex 44.82, Mid 37.94, Base 28.35. Pre-registered harm test: negative-point criteria met 34.0% vs 32.4% for bare Astra (+1.6 points, within the +2.0 bound).
- In plain terms: HealthBench is a set of realistic health conversations, each graded against a checklist written by physicians of what a good answer must include and must avoid. Hard is the 1,000 toughest cases, where most systems score under half. Higher is better; the bare frontier models on the same items are the yardstick.
- Artifacts: [Per-item completions and graded JSONLs on the bench host (public mirror pending)](https://dnai.systems/benchmarks)

### HealthBench Professional: Professional, full set, September 2026 board; every arm through one harness and one grader set (`healthbench-professional-apex`)

- Pipeline / configuration: P6-J; Asha Apex-J, Claude Fable 5.1 composer @4096 (best Asha configuration measured; two trials)
- Deployed tier: Apex tier candidate; not the configuration serving live traffic in September
- Result: **65.1** (Length-adjusted rubric score (the benchmark's official metric), pooled over two trials; CI method none_reported); n = 525; run date 2026-09-14
- Grader: Claude Opus 4.8 (every arm on the board also graded by GPT-5.4 low and gpt-4.1)
- Comparators:
  - GPT-6 Astra (bare, xhigh), length-adjusted, two trials: 67.0 (n=525), basis `same_grader_self_run`: 67.51 / 66.47. Leads the board on the official metric with the lowest harm rate (16%). The gap to Asha is answer length (2.3k vs 4.7k chars); Asha leads raw (73.3 vs 70.9) and red-team.
  - GPT-5.6 Sol (bare, xhigh), two trials: 62.1 (n=525), basis `same_grader_self_run`: 63.03 / 61.18
  - Claude Opus 5 (bare): 58.9 (n=525), basis `same_grader_self_run`
  - Claude Fable 5.1 (bare, adaptive thinking, max effort), two trials: 58.6 (n=525), basis `same_grader_self_run`: 58.76 / 58.5; 12 refusals per trial; highest harm rate of the frontier when it answers (35%)
  - Claude Sonnet 5 (bare): 58.2 (n=524), basis `same_grader_self_run`
  - Claude Opus 4.8 (bare), two trials: 57.2 (n=525), basis `same_grader_self_run`: 56.22 / 58.26
  - GPT-5.6 Luna (bare): 57.0 (n=525), basis `same_grader_self_run`
  - Gemini 3.8 Flash (bare, Vertex): 53.0 (n=525), basis `same_grader_self_run`
  - Physician-written responses (dataset anchor): 50.3 (n=525), basis `same_grader_self_run`: the dataset's physician_response field graded by the same graders; 45.3 under GPT-5.4
  - Glass Health 5.5 (vendor system, agentic search): 46.1 (n=522), basis `same_grader_self_run`
  - Claude Sonnet 4.6 (bare): 43.5 (n=525), basis `same_grader_self_run`
- Paired statistics:
  - Apex-J Fable composer vs bare Fable 5.1 (same backbone as composer), full set: +5.5 pp, n=525, paired t (paper SE), p=0.003
  - Apex-J Fable composer vs Apex-J Opus 4.8 composer, full set: +3.4 pp, n=525, paired t (paper SE), p=0.02
  - Apex-J Astra composer vs bare GPT-6 Astra, same 300 items, GPT-5.4 grader (architecture held to the same model): +3.6 pp, n=300, paired t, length-adjusted, p=0.03
  - Same pair, red-team items only, length-adjusted: +6.6 pp, n=109, paired t, p=see artifact
  - Asha Base vs bare Claude Sonnet 5 (same backbone), red-team items, length-adjusted: +10.1 pp, n=191, paired t, p=see artifact
  - Asha Base vs bare Claude Sonnet 5 (same backbone), all items, length-adjusted: +0.3 pp, n=524, paired t, p=0.88
- Also measured:
  - full L9 concise (full set, 525 items, GPT-5.4 grader): 68.8 vs 44.6 bare (n=525). vs bare gemini31pro on the same items: +24.2 length-adjusted (GPT-5.4, p = 0.00), +25.5 (Opus 4.8). Harm rate 17.7% vs 39.4%. Opus 4.8 grader: 72.7 vs 47.2. adopted as incumbent under the pre-registered rule. Pin cfa13318; 3 trials pooled; read out 2026-09-21.
  - slice freeze concise identity (300-item slice, GPT-5.4 grader): 67.4 vs 69.0 bare (n=300). vs Ladder L9: concise composer style on the same items: -1.6 length-adjusted (GPT-5.4, p = 0.21), -0.8 (Opus 4.8). Harm rate 20.8% vs 19.6%. Opus 4.8 grader: 71.2 vs 72.0. not adopted: inside the 3-point band, gates pass. Pin 1c489dac; one trial; read out 2026-09-20.
  - bare freeze base identity (300-item slice, GPT-5.4 grader): 51.6 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: -0.2 length-adjusted (GPT-5.4, p = 0.93), -1.5 (Opus 4.8). Harm rate 25.0% vs 30.0%. Opus 4.8 grader: 55.0 vs 56.5. adopted as incumbent under the pre-registered rule. Pin n/a; one trial; read out 2026-09-20.
  - full L7 guarded (full set, 525 items, GPT-5.4 grader): 66.2 vs 68.8 bare (n=525). vs full L9 concise on the same items: -2.6 length-adjusted (GPT-5.4, p = 0.01), -3.1 (Opus 4.8). Harm rate 16.7% vs 17.7%. Opus 4.8 grader: 69.6 vs 72.6. not adopted: inside the 3-point band, gates pass. Pin cfa13318; 2 trials pooled; read out 2026-09-20.
  - full L7 guarded (225-item holdout, GPT-5.4 grader): 64.7 vs 65.7 bare (n=225). vs bare GPT-6 Astra on the same items: -1.0 length-adjusted (GPT-5.4, p = 0.64), +0.6 (Opus 4.8). Harm rate 17.2% vs 14.0%. Opus 4.8 grader: 68.6 vs 67.9. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; 2 trials pooled; read out 2026-09-20.
  - full L7 guarded (full set, 525 items, GPT-5.4 grader): 66.2 vs 64.8 bare (n=525). vs bare GPT-6 Astra on the same items: +1.4 length-adjusted (GPT-5.4, p = 0.29), +2.4 (Opus 4.8). Harm rate 16.7% vs 16.0%. Opus 4.8 grader: 69.5 vs 67.1. not adopted: inside the 3-point band, gates pass. Pin cfa13318; 2 trials pooled; read out 2026-09-20.
  - Ladder L9: concise composer style (300-item slice, GPT-5.4 grader): 69.0 vs 64.2 bare (n=300). vs bare GPT-6 Astra on the same items: +4.8 length-adjusted (GPT-5.4, p = 0.00), +4.8 (Opus 4.8). Harm rate 19.6% vs 17.5%. Opus 4.8 grader: 71.4 vs 66.6. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; 2 trials pooled; read out 2026-09-19.
  - Ladder L7: guarded composer style (four harm classes) (300-item slice, GPT-5.4 grader): 68.2 vs 64.2 bare (n=300). vs bare GPT-6 Astra on the same items: +4.0 length-adjusted (GPT-5.4, p = 0.03), +3.5 (Opus 4.8). Harm rate 15.0% vs 17.5%. Opus 4.8 grader: 70.0 vs 66.5. adopted as incumbent under the pre-registered rule. Pin cfa13318; one trial; read out 2026-09-19.
  - full L9 concise (225-item holdout, GPT-5.4 grader): 67.9 vs 65.7 bare (n=225). vs bare GPT-6 Astra on the same items: +2.2 length-adjusted (GPT-5.4, p = 0.23), +4.6 (Opus 4.8). Harm rate 16.5% vs 14.0%. Opus 4.8 grader: 72.6 vs 67.9. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; 3 trials pooled; read out 2026-09-19.
  - full L9 concise (full set, 525 items, GPT-5.4 grader): 68.8 vs 64.8 bare (n=525). vs bare GPT-6 Astra on the same items: +4.0 length-adjusted (GPT-5.4, p = 0.00), +5.4 (Opus 4.8). Harm rate 17.7% vs 16.0%. Opus 4.8 grader: 72.7 vs 67.3. adopted as incumbent under the pre-registered rule. Pin cfa13318; 3 trials pooled; read out 2026-09-19.
  - full L9 concise (225-item holdout, GPT-5.4 grader): 68.6 vs 66.6 bare (n=225). vs bare GPT-6 Astra on the same items: +2.0 length-adjusted (GPT-5.4, p = 0.30), +5.2 (Opus 4.8). Harm rate 15.6% vs 12.9%. Opus 4.8 grader: 73.3 vs 68.1. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; 2 trials pooled; read out 2026-09-19.
  - full L9 concise (full set, 525 items, GPT-5.4 grader): 69.3 vs 64.9 bare (n=525). vs bare GPT-6 Astra on the same items: +4.4 length-adjusted (GPT-5.4, p = 0.00), +6.4 (Opus 4.8). Harm rate 16.9% vs 15.7%. Opus 4.8 grader: 73.3 vs 67.0. adopted as incumbent under the pre-registered rule. Pin cfa13318; 2 trials pooled; read out 2026-09-19.
  - Ladder L9: concise composer style (300-item slice, GPT-5.4 grader): 69.0 vs 62.6 bare (n=300). vs Apex-J, Fable 5.1 composer (E1 baseline, 16 Sep) on the same items: +6.4 length-adjusted (GPT-5.4, p = 0.01), +4.8 (Opus 4.8). Harm rate 19.6% vs 28.3%. Opus 4.8 grader: 71.7 vs 67.0. adopted as incumbent under the pre-registered rule. Pin cfa13318; 2 trials pooled; read out 2026-09-18.
  - Ladder L6: Claude Opus 5 composer (300-item slice, GPT-5.4 grader): 55.3 vs 69.4 bare (n=300). vs Ladder L9: concise composer style on the same items: -14.1 length-adjusted (GPT-5.4, p = 0.00), -11.0 (Opus 4.8). Harm rate 30.0% vs 19.2%. Opus 4.8 grader: 60.6 vs 71.7. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; one trial; read out 2026-09-18.
  - Asha cascade (tier auto: Base / Mid ensemble / Apex by stakes) (300-item slice, GPT-5.4 grader): 51.5 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: -0.3 length-adjusted (GPT-5.4, p = 0.88), -0.4 (Opus 4.8). Harm rate 29.2% vs 30.0%. Opus 4.8 grader: 56.5 vs 56.9. not adopted: inside the 3-point band, gates pass. Pin n/a; one trial; read out 2026-09-18.
  - Ladder L5: query-aware KIL recruiter (300-item slice, GPT-5.4 grader): 69.3 vs 69.4 bare (n=300). vs Ladder L9: concise composer style on the same items: -0.1 length-adjusted (GPT-5.4, p = 0.96), +0.3 (Opus 4.8). Harm rate 19.2% vs 19.2%. Opus 4.8 grader: 71.9 vs 71.7. not adopted: inside the 3-point band, gates pass. Pin cfa13318; one trial; read out 2026-09-18.
  - Ladder L4: dated PubMed live-evidence lane (300-item slice, GPT-5.4 grader): 69.2 vs 69.4 bare (n=300). vs Ladder L9: concise composer style on the same items: -0.2 length-adjusted (GPT-5.4, p = 0.89), +1.5 (Opus 4.8). Harm rate 18.3% vs 19.2%. Opus 4.8 grader: 72.9 vs 71.4. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; one trial; read out 2026-09-18.
  - Ladder L7: guarded composer style (four harm classes) (300-item slice, GPT-5.4 grader): 68.2 vs 69.4 bare (n=300). vs Ladder L9: concise composer style on the same items: -1.2 length-adjusted (GPT-5.4, p = 0.44), -0.9 (Opus 4.8). Harm rate 15.0% vs 19.2%. Opus 4.8 grader: 70.1 vs 71.0. not adopted: inside the 3-point band, gates pass. Pin cfa13318; one trial; read out 2026-09-18.
  - Asha Base, clinician audience + concise (300-item slice, GPT-5.4 grader): 54.9 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: +3.1 length-adjusted (GPT-5.4, p = 0.14), +1.6 (Opus 4.8). Harm rate 28.3% vs 30.0%. Opus 4.8 grader: 57.9 vs 56.4. adopted as incumbent under the pre-registered rule. Pin n/a; one trial; read out 2026-09-18.
  - Asha Base, audience asserted as clinician (300-item slice, GPT-5.4 grader): 52.9 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: +1.1 length-adjusted (GPT-5.4, p = 0.63), +0.7 (Opus 4.8). Harm rate 27.5% vs 30.0%. Opus 4.8 grader: 57.6 vs 56.9. not adopted: inside the 3-point band, gates pass. Pin n/a; one trial; read out 2026-09-18.
  - Ladder L9: concise composer style (300-item slice, GPT-5.4 grader): 69.4 vs 65.8 bare (n=300). vs Round 2 identity: Astra composer on the 17 Sep code (deploy check) on the same items: +3.6 length-adjusted (GPT-5.4, p = 0.01), +3.6 (Opus 4.8). Harm rate 19.2% vs 17.5%. Opus 4.8 grader: 71.3 vs 67.7. adopted as incumbent under the pre-registered rule. Pin cfa13318; one trial; read out 2026-09-18.
  - Asha Base, translate-and-correct on unsafe handouts (300-item slice, GPT-5.4 grader): 52.5 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: +0.7 length-adjusted (GPT-5.4, p = 0.75), -0.8 (Opus 4.8). Harm rate 23.3% vs 30.0%. Opus 4.8 grader: 55.9 vs 56.8. adopted as incumbent under the pre-registered rule. Pin n/a; one trial; read out 2026-09-18.
  - Asha Base, labelled recall on retrieval miss (300-item slice, GPT-5.4 grader): 54.4 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: +2.5 length-adjusted (GPT-5.4, p = 0.25), +0.1 (Opus 4.8). Harm rate 26.7% vs 30.0%. Opus 4.8 grader: 56.6 vs 56.5. not adopted: inside the 3-point band, gates pass. Pin n/a; one trial; read out 2026-09-18.
  - Ladder L8: audience asserted as clinician (300-item slice, GPT-5.4 grader): 59.8 vs 65.8 bare (n=300). vs Round 2 identity: Astra composer on the 17 Sep code (deploy check) on the same items: -6.0 length-adjusted (GPT-5.4, p = 0.00), -5.4 (Opus 4.8). Harm rate 19.2% vs 17.5%. Opus 4.8 grader: 62.9 vs 68.4. rejected: a gate failed or the score fell 3 points or more. Pin cfa13318; one trial; read out 2026-09-18.
  - Asha Base, concise style (300-item slice, GPT-5.4 grader): 52.4 vs 51.8 bare (n=300). vs Asha Base on the 17 Sep code (Base identity) on the same items: +0.5 length-adjusted (GPT-5.4, p = 0.80), +2.5 (Opus 4.8). Harm rate 31.7% vs 30.0%. Opus 4.8 grader: 59.1 vs 56.6. not adopted: inside the 3-point band, gates pass. Pin n/a; one trial; read out 2026-09-18.
  - Round 2 identity: Astra composer on the 17 Sep code (deploy check) (300-item slice, GPT-5.4 grader): 65.8 vs 67.2 bare (n=300). vs Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) on the same items: -1.4 length-adjusted (GPT-5.4, p = 0.30), -1.4 (Opus 4.8). Harm rate 17.5% vs 17.5%. Opus 4.8 grader: 68.6 vs 70.0. not adopted: inside the 3-point band, gates pass. Pin cfa13318; one trial; read out 2026-09-18.
  - Asha Base on the 17 Sep code (Base identity) (300-item slice, GPT-5.4 grader): 51.8 vs 53.1 bare (n=300). vs Asha Base (live lane, 16 Sep) on the same items: -1.2 length-adjusted (GPT-5.4, p = 0.59), -1.0 (Opus 4.8). Harm rate 30.0% vs 26.7%. Opus 4.8 grader: 56.6 vs 57.6. rejected: a gate failed or the score fell 3 points or more. Pin n/a; one trial; read out 2026-09-18.
  - Ladder L3: every panel agent on Claude Opus 5 (300-item slice, GPT-5.4 grader): 66.5 vs 67.2 bare (n=300). vs Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) on the same items: -0.7 length-adjusted (GPT-5.4, p = 0.58), +0.2 (Opus 4.8). Harm rate 18.3% vs 17.5%. Opus 4.8 grader: 69.5 vs 69.4. not adopted: inside the 3-point band, gates pass. Pin 1c2b7fc6, cab1d043; one trial; read out 2026-09-17.
  - Ladder L2: current-affairs and India corpora excluded from retrieval (300-item slice, GPT-5.4 grader): 65.5 vs 67.2 bare (n=300). vs Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) on the same items: -1.7 length-adjusted (GPT-5.4, p = 0.25), -2.7 (Opus 4.8). Harm rate 15.8% vs 17.5%. Opus 4.8 grader: 66.7 vs 69.4. not adopted: inside the 3-point band, gates pass. Pin cab1d043; one trial; read out 2026-09-17.
  - Apex-J, Fable composer, identity re-run on the 17 Sep pin (deploy check) (300-item slice, GPT-5.4 grader): 62.0 vs 62.6 bare (n=300). vs Apex-J, Fable 5.1 composer (E1 baseline, 16 Sep) on the same items: -0.6 length-adjusted (GPT-5.4, p = 0.74), +0.5 (Opus 4.8). Harm rate 31.7% vs 28.3%. Opus 4.8 grader: 67.4 vs 66.9. rejected: a gate failed or the score fell 3 points or more. Pin cab1d043; one trial; read out 2026-09-17.
  - Apex-J, Fable 5.1 composer, concise style, clean-pin re-run (300-item slice, GPT-5.4 grader): 68.3 vs 67.2 bare (n=300). vs Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) on the same items: +1.1 length-adjusted (GPT-5.4, p = 0.68), +4.9 (Opus 4.8). Harm rate 28.3% vs 17.5%. Opus 4.8 grader: 74.8 vs 69.9. rejected: a gate failed or the score fell 3 points or more. Pin cab1d043; one trial; read out 2026-09-17.
  - Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) (300-item slice, GPT-5.4 grader): 67.2 vs 62.6 bare (n=300). vs Apex-J, Fable 5.1 composer (E1 baseline, 16 Sep) on the same items: +4.6 length-adjusted (GPT-5.4, p = 0.07), +1.8 (Opus 4.8). Harm rate 17.5% vs 28.3%. Opus 4.8 grader: 69.4 vs 67.5. adopted as incumbent under the pre-registered rule. Pin cab1d043; one trial; read out 2026-09-17.
  - Apex-J, GPT-6 Astra composer, concise style (E6) (300-item slice, GPT-5.4 grader): 69.4 vs 67.2 bare (n=300). vs Apex-J, GPT-6 Astra composer (E3; ceiling ladder incumbent) on the same items: +2.2 length-adjusted (GPT-5.4, p = 0.08), +3.1 (Opus 4.8). Harm rate 19.2% vs 17.5%. Opus 4.8 grader: 72.5 vs 69.4. not adopted: inside the 3-point band, gates pass. Pin cab1d043; one trial; read out 2026-09-17.
  - Apex-J, Fable 5.1 composer, concise style (E2; straddled a restart, record only) (300-item slice, GPT-5.4 grader): 67.7 vs 62.6 bare (n=300). vs Apex-J, Fable 5.1 composer (E1 baseline, 16 Sep) on the same items: +5.1 length-adjusted (GPT-5.4, p = 0.01), +4.6 (Opus 4.8). Harm rate 29.2% vs 28.3%. Opus 4.8 grader: 71.5 vs 66.9. rejected: a gate failed or the score fell 3 points or more. Pin 2165d45a, cab1d043; one trial; read out 2026-09-17.
- Notes: Every arm on the board, ours and the bare frontier models, went through one harness and three graders, so the ranking is like-for-like. On the September board (Asha arms on the 12 September build, Fable 5.1 composer) GPT-6 Astra leads on the official length-adjusted metric and Asha Apex-J is second, ahead on raw content and on red-team items at a higher harm rate than Astra. We publish the ordering as measured. Since then a ceiling ladder has run on a 300-item stratified slice of this set, one trial per arm, every arm on one recorded api process (the pin) and paired item by item against the incumbent under a pre-registered rule: adopt on 3 points or more, or on a clear harm reduction at equal score, with harm, red-team, empty-answer, refusal and grader-agreement gates passing. Round 1 (17 Sep) moved the composer to GPT-6 Astra. Round 2 (18 Sep, on the 17 Sep code: clinician register, language, memory scope) adopted the concise composer style (+3.6 length-adjusted, p=0.01, harm within gate); the guarded style, a dated PubMed live-evidence lane and the query-aware retriever each read inside the noise band against that incumbent, and asserting a clinician audience on this physician-written set regressed on red-team items. The Opus 5 composer arm is running. On the Base tier the same ladder adopted two prompt levers: clinician register with the concise style (+3.1) and a translate-and-correct rule for unsafe handouts, adopted on safety alone (harm down 6.7 points overall and 9.3 on red-team items at equal score). The live cascade, which sends 32 of these 300 items above Base by gravity, read level with Base overall; in the 25-item Mid band the ensemble scored below Base on all three graders, which is the evidence the Mid-floor decision now rests on. Slice results are exploratory by design and do not replace the board. When round 2 closes, the incumbent runs the full 525 items twice against bare GPT-6 Astra twice on the same pin and graders; that pre-freeze number is listed here when it lands. The code-freeze battery (22 to 25 September, Professional 525 x 2 for Base, Mid and Apex on the frozen build) produces the number of record and replaces this row. Per-item Professional data are withheld at OpenAI's no-publish request, so this row is tier C until the freeze artifacts are released.
- In plain terms: The 525 questions a clinician asks in practice (dosing, differentials, management), graded against physician checklists. The official score penalizes long answers, so a system cannot win by saying more. Every system on this board was scored by the same grader in the same run, which is what makes the ranking fair. The rows under Also measured are one experiment at a time on the same 300 questions: each row names what changed, what it was compared with, and whether the change was adopted, left alone, or rejected under a rule written before the run. The current best configuration wraps our architecture around the leading model and asks it to answer briefly; it leads that bare model on these questions at the same rate of harmful statements.
- Artifacts: [June 2026 configs and aggregate results (public repo, professional/)](https://github.com/EndlessRay/asha-healthbench-2026-06-26/tree/main/professional); [Preprint (Research Square rs-10206806)](https://www.researchsquare.com/article/rs-10206806/v1)

### HealthBench, 500-item sample (Vishwanath et al. harness): Independent study's 500-item sample (`healthbench-500-independent`)

- Pipeline / configuration: Apex-J; Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on), graded in the study's public pipeline
- Deployed tier: Apex tier of the production cascade (APEX_TIER_PIPELINE=apex_j)
- Result: **63.8** (Rubric score in the study's pipeline (points achieved / points possible, pooled); CI method none_reported); n = 500; run date 2026-09-23
- Grader: three-judge panel, majority per criterion (anthropic-claude-4-6-opus, google-gemini-3-1-pro-preview, openai-gpt-5-2): the published study's configuration, run in its own pipeline
- Comparators:
  - OpenEvidence: 62.6, basis `literature`: as reported by Vishwanath et al. (Nat Med 2026), same three-judge panel configuration, same 500 items
  - UpToDate Expert AI: 61.3, basis `literature`: as reported by Vishwanath et al. (Nat Med 2026), same three-judge panel configuration, same 500 items
  - GPT-6 Astra (bare, retrieval off): 54.9 (n=500), basis `same_grader_self_run`: same 500 answers graded by the same panel in the same pipeline; the composer backbone without the Asha layer
  - Asha Apex (P6, June 2026 build): 66.8 (n=500), basis `same_grader_self_run`: June 2026 answers, two of the study's three judges (Claude Opus 4.6 + Gemini 3.1 Pro Preview); lineage
- Paired statistics:
  - Grader stability: today's gpt-4.1 vs June gpt-4.1 on identical June-29 completions (study pipeline, 500 items): -0.3 pp, n=500, same completions, points achieved / possible, p=n/a
- Also measured:
  - Frozen Apex-J on the same 500, gpt-4.1 single, HealthBench per-example mean (from the 5,000-item run): 61.6 vs 53.2 bare (n=500). Ties the 500 to the 5,000 main grade; not the study's grader (the panel row above is).
  - Apex-J, GPT-5.4 grader (seed-62 500): 56.4 vs 49.1 bare (n=500). Sensitivity grader; official HealthBench grading is gpt-4.1. Harm proxy 20.8%. Paired vs bare Astra +7.3 pp.
  - Apex-J, Claude Opus 4.8 grader (seed-62 500): 67.1 vs 58.7 bare (n=495). Sensitivity grader; official HealthBench grading is gpt-4.1. Harm proxy 19.6%. Paired vs bare Astra +8.6 pp.
- Notes: The served configuration (frozen Apex-J) answered the study's 500-item sample inside the 5,000-item run; those 500 answers were graded in the study's own public pipeline with its published three-judge panel (majority per criterion), so the comparison with OpenEvidence and UpToDate Expert AI is on the study's own grader and items. Bare GPT-6 Astra is graded by the same panel on the same answers set. History: the 10 Sep independent run (Airpixels) scored 66.6 under gpt-4.1 single; the June P6 answers scored 66.8 under two of the three judges and 71.0 with gpt-4.1 as the third; grader stability of gpt-4.1 was 72.3 vs 72.6 on identical completions. Commercial-tool values are the study's, not ours, and say nothing about those tools outside this item sample.
- In plain terms: An independent research group published a 500-question sample and a scoring pipeline to compare commercial clinical tools such as OpenEvidence and UpToDate Expert AI. The model that ships on 1 October answered those 500 questions and was scored inside the study's own pipeline with the study's own three-judge panel, so the comparison is on their terms.
- Artifacts: [Preprint Table 4 and the study's pipeline (Research Square rs-10206806)](https://www.researchsquare.com/article/rs-10206806/v1)

### MedQA USMLE, 4-option test split: Canonical test split, SHA-256 locked, single shot, same day across arms (`medqa-usmle-locked`)

- Pipeline / configuration: P2; Deployed single-call engine
- Deployed tier: Base tier (the live single-call engine)
- Result: **95.5** [94.2, 96.5] (Accuracy; CI method wilson); n = 1273; run date 2026-05-04
- Grader: None (deterministic letter match, strict regex)
- Comparators:
  - Claude Opus 4.5: 94.7 (n=1273), basis `same_grader_self_run`: paired McNemar vs Asha p = 0.228, indistinguishable
  - o4-mini-high: 93.8 (n=1273), basis `same_grader_self_run`
  - Gemini 3.1 Pro Preview: 92.3 (n=1273), basis `same_grader_self_run`: paired McNemar vs Asha p = 2.0e-5, OR 2.64 [1.67, 4.18]; 5.58% parse failures vs 0 for Asha
  - GPT-4o: 91.6 (n=1273), basis `same_grader_self_run`
- Also measured:
  - Independent re-run of the live system (Airpixels, September 2026, strict extractor): 92.5 (n=1273). 1177/1273, 13 unparsed; our own September re-run 93.64
- Notes: Locked head-to-head: every arm answered the same 1,273 items on the same day, so question drift and grader variation are controlled across arms. Zero parse failures for Asha on the May 2026 run. September re-runs of the live system read 92.5 to 93.6; the code-freeze battery re-runs MedQA with a shared extractor.
- In plain terms: Multiple-choice questions from the US medical licensing exam. Every system answered the same 1,273 questions on the same day and the score is the share answered correctly. A floor for medical knowledge that frontier models have nearly saturated; the paired comparisons are the useful part.
- Artifacts: [Per-item results, dataset hash, scripts (public repo, medqa-2026-05-04/)](https://github.com/EndlessRay/asha-bench-public/tree/main/medqa-2026-05-04)

### psychosis-bench (Au Yeung et al. 2025): Full protocol; 96 intervention-eligible turns per arm (`psychosis-bench-sis`)

- Pipeline / configuration: P2; Deployed engine, backbone gemini-2.5-flash
- Deployed tier: Base tier (the live engine), same backbone as the bare arm
- Result: **95.8** [89.8, 98.4] (Safe-intervention rate (SIS), higher is safer; CI method wilson); n = 96; run date 2026-05-11
- Grader: gpt-4o-mini (the benchmark's protocol judge); Claude Haiku 4.5 as second judge
- Comparators:
  - Bare gemini-2.5-flash (the May 2026 backbone, no architecture): 30.2 (n=96), basis `same_grader_self_run`: Fisher exact two-sided P = 4.0e-23, odds ratio 53 [18, 158]. Same backbone as the Asha arm, so the gap is the architecture.
  - Bare Gemini 3.6 Flash (a current bare model, independent run, September 2026): 93.8 (n=96), basis `independent_validator`: Current bare frontier models score far higher on this protocol than the May 2026 backbone did; the 30.2 to 95.8 gap is a same-backbone measurement from May.
  - Bare GLM-5.2 (open weights): 80.2 (n=96), basis `same_grader_self_run`: DCS 0.31 / HES 0.31
- Also measured:
  - Deployed engine re-run by the independent validator (Airpixels, September 2026): 96.9 (n=96). 93/96
  - Delusion-confirmation score (DCS), lower is safer: 0.4 vs 1.2 bare. 3.43x lower; scenario-paired bootstrap 95% CI [2.15, 6.13]
  - Harm-enablement score (HES), lower is safer: 0.1 vs 0.8 bare. 7.9x lower
  - Asha Apex (P6) SIS: 97.9 (n=96). 94/96; DCS 0.02, HES 0.00
  - Frozen Apex-J (freeze-2026-09-20: Astra composer, concise, FENG) SIS: 95.8 (n=96). 92/96; DCS 0.146, HES 0.021; the four misses are one scenario (secret_project_implicit, turns 7-9 and 12) where the answer refused the harmful instructions but did not redirect; protocol judge gpt-4o-mini; run 2026-09-20 on the lane
  - Asha Base, same run (20 Sep) SIS: 100.0 (n=96). 96/96; DCS 0.118, HES 0.135
  - Bare Claude Sonnet 4.5, same run (20 Sep) SIS: 100.0 (n=96). 96/96; DCS 0.007, HES 0.000. Current bare frontier models match Asha on this protocol; the May held-backbone gap (30.2% for bare gemini-2.5-flash) is a statement about what the architecture adds to a given backbone, not about frontier models today
- Notes: The backbone is held fixed and only the surrounding architecture varies, so the May 2026 gain is attributable to the architecture. Both pre-registered hypotheses (DCS, SIS) pass; the two judges agree on the direction of every metric, and inter-judge agreement fell below the pre-registered gate (kappa 0.25), which the pre-registration records as an inconclusive formal verdict. n=96 is fixed by the protocol (16 scenarios x 12 turns, 96 intervention-eligible turns per arm). Re-run 2026-09-20 on the frozen Apex-J with the same protocol and judge: SIS 95.8% [89.8, 98.4], DCS 0.146, HES 0.021; Asha Base 100%; bare Claude Sonnet 4.5 100% with DCS 0.007 and HES 0. The crisis claim to make is the held-backbone one (same model, 30% without Asha, 96% with); against today's bare frontier models the protocol reads parity, not superiority.
- In plain terms: Scripted 12-turn conversations in which a user slides toward delusional beliefs and asks for things that could cause harm. The safety score is how often the system intervened safely when it should have, instead of agreeing along. The same underlying model was tested bare and inside Asha, so the difference is the architecture.
- Artifacts: [Per-turn judge outputs, scenarios, pre-registration (public repo, psychosis-bench-2026-05-11/)](https://github.com/EndlessRay/asha-bench-public/tree/main/psychosis-bench-2026-05-11); [Attribution study: Flash to Pro tier jump gives no safety lift](https://github.com/EndlessRay/asha-bench-public/tree/main/psychosis-attribution-2026-05-12)

### Enclomiphene-bench v1.0, patient arm (psychosis-bench protocol): Full protocol; 36 intervention-eligible turns per arm (`enclomiphene-bench-sis`)

- Pipeline / configuration: P2; Deployed engine, anthropic_routed backbone (claude-sonnet-4-6 / claude-opus-4-8 by gravity)
- Deployed tier: Production cascade as routed
- Result: **100.0** [90.4, 100.0] (Safe-intervention rate (SIS), higher is safer; CI method wilson); n = 36; run date 2026-09-18
- Grader: gpt-4o-mini (the psychosis-bench protocol judge); Claude Haiku 4.5 as second judge, same 36/36
- Comparators:
  - Bare Claude Sonnet 4.5: 100.0 (n=36), basis `same_grader_self_run`: 36/36 under both judges; HES 0.000 under both
  - Bare GPT-5 (reasoning_effort low): 94.4 (n=36), basis `same_grader_self_run`: Judge A; Judge B 31/36
  - Bare Gemini 3.5 Flash (Vertex): 86.1 (n=36), basis `same_grader_self_run`: Judge A; Judge B 33/36. HES 0.917 with 16 HES = 2 turns under Judge A
- Also measured:
  - Emergency turns with explicit emergency direction: 100.0 (n=4). 4/4: calf swelling with dyspnea, chest pressure twice, a child's monocular visual loss
  - Suicidal-ideation turns with crisis direction: 100.0 (n=3). 3/3, 988 named each time
  - Harm-enablement score (HES), lower is safer: 0.3. Judge A; Judge B 0.417. Judges disagree on HES magnitude for three of four arms (kappa 0.03 to 0.29), so HES is not used to rank arms in this release. Pre-registered H1 fails under Judge A on three turns that Judge B scores 0 and that read as explicit refusals.
- Notes: Single-topic longitudinal safety set on the 2026 compounded-enclomiphene fad (young eugonadal men, telehealth at about $90 a month, 'I don't take testosterone'). Asha and bare Claude Sonnet 4.5 both intervene on every eligible turn; the separation between Asha and the bare models appears in the clinician red-team arm (appendix). Per-turn artifacts for all four arms and both judges are public.
- Artifacts: [Per-turn outputs for both judges and all four arms, question files, stats script (public repo, enclomiphene-bench-2026-09-18/)](https://github.com/EndlessRay/asha-bench-public/tree/main/enclomiphene-bench-2026-09-18); [Benchmark design and pre-registration (monorepo, scripts/audits/enclomiphene_bench/README.md)](https://github.com/EndlessRay/asha-bench-public/blob/main/enclomiphene-bench-2026-09-18/README.md)

### Locked pediatric AOM chart (Hobbs, dochobbs/aom-chart packet v5): Locked 24-month stem (`aom-locked-chart-cds`)

- Pipeline / configuration: P2; Deployed production build, serial runs, 2026-08-26
- Deployed tier: Live engine
- Result: **100.0** [78.5, 100.0] (Runs passing every scored dimension (boundary arithmetic, weight-based dose, duration, declared assumptions, no invented chart facts); CI method wilson); n = 14; run date 2026-08-26
- Grader: Rubric applied by us to verbatim traces; the benchmark author's adjudication is pending and owns the scoreboard
- Also measured:
  - Identity-variant cells with invariant plan (insurance, race, name, caregiver age, occupation, interpreter): 100.0 (n=36). 36/36; zero adverse reliability inferences
  - 18-month counter-stem (rule generalizes rather than memorizes): 100.0 (n=5). 5/5 kept the 10-day course and the 6-to-23-month stratum
  - Casual-phrasing probe: 100.0 (n=4). 4/4
- Notes: Self-run receipts on a clinician's public locked chart; the author adjudicates and owns the scoreboard. Known imperfection, quantified in the traces: in roughly 1 to 2 of every 10 runs the amoxicillin-clavulanate trigger check is phrased as an assertion plus a confirm-with-caregiver directive rather than the stricter declared form. n is set by the chart; the interval is shown for that reason.
- In plain terms: A pediatrician published a locked chart of a two-year-old with an ear infection and asked AI systems for the plan. Passing means correct age arithmetic, correct weight-based dose and duration, no invented chart facts, and the same plan whatever the child's insurance, race, or name. The chart's author owns the scoreboard.
- Artifacts: [Verbatim traces and scoring (public repo)](https://github.com/EndlessRay/asha-aom-chart-2026-08); [The benchmark author's chart and packet](https://github.com/dochobbs/aom-chart)

### HealthBench standard: Standard, full set (`healthbench-standard`)

- Pipeline / configuration: Apex-J; Asha Apex-J, frozen 20 Sep 2026 (GPT-6 Astra composer, concise style, FENG on, KIL on)
- Deployed tier: Apex tier of the production cascade (APEX_TIER_PIPELINE=apex_j)
- Result: **60.7** [59.8, 61.5] (Rubric score; CI method bootstrap); n = 5000; run date 2026-09-21
- Grader: gpt-4.1 (the official HealthBench grader)
- Pre-registered harm test: pre-registered (CEILING_5000_GATE.md, A3): harm proxy vs bare Astra within +2.0 points on the 5,000: +2.8 points, bound 2.0, NOT met
- Comparators:
  - GPT-6 Astra (bare, retrieval off): 52.7 (n=5000), basis `same_grader_self_run`: same harness, same items, same grader; the composer backbone of Apex-J without the Asha layer; run 19 Sep 2026
  - Asha Mid (P5, June 2026 build): 60.6 (n=5000), basis `same_grader_self_run`: June 2026 run in the same harness (lineage; a different build, no longer served)
  - Asha Base (P2, June 2026 build): 44.1 (n=5000), basis `same_grader_self_run`: June 2026 run in the same harness (lineage; a different build, no longer served)
- Paired statistics:
  - Apex-J vs bare GPT-6 Astra, same 5,000 items: +8.0 pp, W/L/T 2618 / 1162 / 1220, n=5000, paired t-test, two-sided; exact sign test p = 5.2e-127, p=6.9e-110
- Also measured:
  - Apex-J, GPT-5.4 grader (full 5,000): 55.2 vs 48.1 bare (n=5000). Sensitivity grader; official HealthBench grading is gpt-4.1. Harm proxy 22.0%. Paired vs bare Astra +7.1 pp.
  - Apex-J, Claude Opus 4.8 grader (full 5,000): 65.8 vs 57.7 bare (n=4932). Sensitivity grader; official HealthBench grading is gpt-4.1. Harm proxy 20.9%. Paired vs bare Astra +8.3 pp.
- Notes: The served configuration (frozen Apex-J) on the full 5,000-item Standard set, graded by gpt-4.1. Harm proxy (negative-point criteria met) 29.8%, 0 empty answers. Bare GPT-6 Astra is the composer backbone without the Asha layer, run on the same items with retrieval off; the paired difference is the architecture. The June 2026 Mid and Base rows stay as lineage: different builds, not the served tier. Standard and Hard are different benchmarks; never compare across sets. Grading paused during the 22 Sep vendor credit outage; rows that carried 429 errors were discarded and re-graded, no partial rows are counted. Per-theme and per-axis scores are in the register (breakdown). Pre-registered harm test NOT met: negative-point criteria met 29.8% vs 27.0% for bare Astra (+2.8 points, bound +2.0). Fuller answers trip more negative-point criteria while scoring higher on every theme; per the gate document the number ships with this caveat and the freeze is under review before any launch claim.
- In plain terms: The full 5,000-conversation HealthBench set, easier on average than the Hard subset. Same physician checklists, same official grader. This is the model that ships on 1 October, measured once, frozen, against its own bare backbone on the same questions. Standard and Hard scores are never compared with each other.
- Artifacts: [Per-item completions and graded JSONLs on the bench host (public mirror pending)](https://dnai.systems/benchmarks)

### KaBLE, belief-reasoning subset: 220-question subset spanning first-person, third-person, and recursive belief (`kable-belief-220`)

- Pipeline / configuration: P2; Deployed single-call engine
- Deployed tier: Base tier (the live single-call engine)
- Result: **97.7** [94.8, 99.0] (Accuracy, answer-key matched; CI method wilson); n = 220; run date 2026-06
- Grader: None (answer-key match)
- Comparators:
  - GPT-4o, first-person false belief (literature): 64.4, basis `literature`: Suzgun et al. 2025, on the full KaBLE task, a different item set; reference point only
  - 15-model average (literature): 54.4, basis `literature`: Suzgun et al. 2025; reference point only
- Also measured:
  - KaBLE BioMedicine subset, independent run (Airpixels, September 2026): 97.6 (n=1050). 1025/1050 scored; a different subset from the 220
- Notes: Literature reference points are on the published KaBLE task, a different item set from our 220-question subset, so they are context and never a like-for-like bar. Per-item record is internal; public release pending.
- In plain terms: Tests whether a system keeps what a person believes separate from what is true, for example a user who says they believe something false. The score is the share of belief-reasoning questions answered correctly. Bare language models tend to adopt the user's belief.
- Artifacts: [Preprint Table 4 and Section 5 (Research Square rs-10206806)](https://www.researchsquare.com/article/rs-10206806/v1)

## Appendix: small-n scenarios


Small samples (below the register's n threshold): reported with intervals where the metric is a proportion, never as headline claims.

| Benchmark | Set | n | Configuration | Result | Comparators | Grader |
|---|---|---|---|---|---|---|
| MedHELM: aci_bench | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **4.87 / 5** | 4.36 / 5 Asha Base (P2, dnai/asha), same run; 4.86 / 5 GPT-5, published v4.0.0 field (mid-2025 models), as published | LLM jury, 1 to 5 scale (MedHELM protocol) |
| MedHELM: mtsamples_replicate | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **4.86 / 5** | 4.56 / 5 Asha Base (P2, dnai/asha), same run; 4.72 / 5 GPT-5 mini, published v4.0.0 field (mid-2025 models), as published | LLM jury, 1 to 5 scale (MedHELM protocol) |
| MedHELM: medication_qa | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **4.76 / 5** | 4.60 / 5 Asha Base (P2, dnai/asha), same run; 4.84 / 5 Gemini 2.5 Pro, published v4.0.0 field (mid-2025 models), as published | LLM jury, 1 to 5 scale (MedHELM protocol) |
| MedHELM: medi_qa | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **4.94 / 5** | 4.86 / 5 Asha Base (P2, dnai/asha), same run; 4.97 / 5 Gemini 2.5 Pro, published v4.0.0 field (mid-2025 models), as published | LLM jury, 1 to 5 scale (MedHELM protocol) |
| MedHELM: medcalc_bench | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **40.0** [24.6, 57.7] | 13.3 Asha Base (P2, dnai/asha), same run, 4/30; 34.8 Gemini 2.5 Pro, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: medhallu | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **93.3** [78.7, 98.2] | 96.7 Asha Base (P2, dnai/asha), same run, 29/30; 92.6 Claude 3.5 Sonnet, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: pubmed_qa | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **66.7** [48.8, 80.8] | 60.0 Asha Base (P2, dnai/asha), same run, 18/30; 76.4 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: ehr_sql | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **20.0** [9.5, 37.3] | 13.3 Asha Base (P2, dnai/asha), same run, 4/30; 32.0 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: medec | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **63.3** [45.5, 78.1] | 60.0 Asha Base (P2, dnai/asha), same run, 18/30 | Deterministic scenario metric (MedHELM) |
| MedHELM: med_qa | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **83.3** [66.4, 92.7] | 83.3 Asha Base (P2, dnai/asha), same run, 25/30; 96.8 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: race_based_med | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **80.0** [62.7, 90.5] | 83.3 Asha Base (P2, dnai/asha), same run, 25/30; 91.6 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: head_qa | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **86.7** [70.3, 94.7] | 93.3 Asha Base (P2, dnai/asha), same run, 28/30; 93.7 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| MedHELM: medbullets | Efficient pass, 30-item sample per scenario | 30 | Asha Apex (dnai/asha-apex) | **46.7** [30.2, 63.9] | 56.7 Asha Base (P2, dnai/asha), same run, 17/30; 87.0 published top, published v4.0.0 field (mid-2025 models), as published | Deterministic scenario metric (MedHELM) |
| Enclomiphene-bench v1.0, clinician red-team arm | 18 adversarial clinician prompts, 116 rubric items with negative points, HealthBench scoring | 18 | Deployed engine, anthropic_routed backbone, KIL on (no enclomiphene-specific source in the corpus at run time) | **0.6** [0.5, 0.7] | 0.5 Bare Gemini 3.5 Flash (Vertex); 0.5 Bare GPT-5 (reasoning_effort low); 0.4 Bare Claude Sonnet 4.5 | gpt-4.1 (the official HealthBench grader) |

## External validation

- Validator: Airpixels Innovations LLP
- Protocol: Pre-registered tolerance protocol: environment reproduction, harness verification, artifact recomputation, fresh runs on the pinned route
- Status: Package 1 accepted 2026-08-27; validation note signed 2026-09-10.
- Confirmed: HealthBench Hard: Apex 44.82, Mid 37.94, Base 28.35 (artifact recompute, n=1,000 / 898 / 1,000); paired Mid-vs-Base +9.7 pp (p=1.0e-19), Apex-vs-Mid +6.6 pp (p=4.1e-7); HealthBench Standard: Mid 60.59, Base 44.06 (n=5,000); MedQA artifact 95.52 (1216/1273), exact; locked-split SHA-256 exact; psychosis-bench deployed engine, fresh run 96.9 (93/96); Corpus commitment: hash confirmed over 20 collections, 111,094,821 vectors

## Reproduce

- [HealthBench: harness, configs, graded data, pipeline glossary](https://github.com/EndlessRay/asha-healthbench-2026-06-26)
- [MedQA, psychosis-bench, META_CORRECT: bit-exact public artifacts](https://github.com/EndlessRay/asha-bench-public)
- [Locked pediatric AOM chart receipts](https://github.com/EndlessRay/asha-aom-chart-2026-08)
- [Preprint, 24 pp (Research Square rs-10206806)](https://www.researchsquare.com/article/rs-10206806/v1)
- [Live corpus commitment (hash over the knowledge corpus the benchmarks ran against)](https://api.askasha.org/api/audit/corpus-state/public)
- [US Patent 12,555,008 B1 (the architecture the lift comes from)](https://patents.google.com/patent/US12555008B1)
- [A2A agent card (query any agent programmatically)](https://api.askasha.org/.well-known/agent-card.json)
