# DNAi models: cards, benchmarks, artifacts

Public record of the AI systems DNAi Systems ships, what each one is, and what each has been measured to do. Asha ([askasha.org](https://askasha.org)) is the medical agent; Harley, Artha, Sage, Polymath, Lyra, Leo, Mira, Ren, Arohi and Ray are the other agents of the fleet, reachable over the A2A protocol.

Three rules govern everything here. A number is published only with its set size, its grader and a per-item artifact anyone can re-grade. Comparators are labeled by how they were scored (same grader in our run, independent validator, vendor self-reported, as published). When a claim is overturned or restated, the correction is written in the same history, next to the claim.

## Contents

| Path | What |
|---|---|
| [`MODEL_CARDS.md`](MODEL_CARDS.md) | The four Asha tiers (Base, Mid, Apex P6 lineage, Apex-J frozen and served), shared components, limitations, API names |
| [`BENCHMARKS.md`](BENCHMARKS.md) | The public benchmark register rendered as a document, generated from the same JSON the live page serves |
| [`benchmarks/register/`](benchmarks/register/) | Dated copies of the register JSON ([dnai.systems/benchmarks.json](https://dnai.systems/benchmarks.json)) |
| [`benchmarks/healthbench-5000-2026-09-20/`](benchmarks/healthbench-5000-2026-09-20/) | Per-item artifacts of the launch measurement: the frozen Asha Apex-J and its bare backbone on the full 5,000-item HealthBench set under three graders, the Vishwanath 500 under the study's published three-judge panel, identity and style checks, SHA-256 manifest |
| [`tools/`](tools/) | The renderer that turns the register JSON into `BENCHMARKS.md` |

Earlier artifact sets live in their own repositories and are linked from the register: [asha-healthbench-2026-06-26](https://github.com/EndlessRay/asha-healthbench-2026-06-26) (June 2026 HealthBench runs, pipeline glossary, preprint), [asha-bench-public](https://github.com/EndlessRay/asha-bench-public) (MedQA, Psychosis Bench, META_CORRECT), [asha-aom-chart-2026-08](https://github.com/EndlessRay/asha-aom-chart-2026-08) (locked chart traces).

## What ships on 1 October 2026

The served Apex tier is Asha Apex-J, frozen 20 September 2026 (tag `freeze-2026-09-20`). Against its own bare backbone (GPT-6 Astra, no retrieval, no system prompt) on the same items and under the official HealthBench grader: **60.7 vs 52.7** on the full 5,000 (+8.0, p = 7e-110) and **42.0 vs 29.4** on Hard 1,000 (+12.6). On the Vishwanath et al. 500-item sample, graded in the study's own pipeline with its published three-judge panel: **63.8**, against OpenEvidence 62.6 and UpToDate Expert AI 61.3 as the study reports them, and 54.9 for the bare backbone under the same panel. Zero refusals across every set.

Two things the same artifacts show and the cards state: the June 2026 Apex (P6) build scored higher on raw rubric metrics than the frozen build (68.4 vs 63.8 on the 500 under the same panel; 44.8 vs 42.0 on Hard under the same grader), because its answers were longer and more complete; and the frozen build triggers more negative-point criteria than the bare backbone under gpt-4.1 (+2.8 points on the 5,000, mostly length and over-detail criteria) while triggering fewer under GPT-5.4 and Claude Opus 4.8. Both are on the register rows next to the numbers.

## Architecture, in one paragraph

Asha is neurosymbolic: vendor language models produce language; the symbolic layer around them retrieves evidence from a curated corpus (Knowledge Integration Layer), falsifies extracted claims against that corpus (FENG), runs a panel of specialist agents to a quorum, composes their drafts under a domain composer with a grounding check, and applies safety gates before and after generation. No model is fine-tuned. The public falsifiability surface for this architecture is the paired difference between the full system and its bare backbone on the same items under the same grader, which is how every headline row is reported. Patent: US 12,555,008 B1; the specification is held internally and is not in this repository.

## What is not here

System prompts, agent charters, pipeline code, corpus composition beyond collection counts, cost internals, and anything that would let a third party reconstruct the pipeline. The artifacts are complete for re-grading and for checking every number we publish; they are not a build kit.

## Use and citation

Re-grade, recompute, quote, and criticize with attribution to DNAi Systems and a link to this repository. Cite the register at [dnai.systems/benchmarks](https://dnai.systems/benchmarks) for the current numbers; this repository holds dated snapshots and the artifacts behind them.

Contact: open an issue in this repository.
