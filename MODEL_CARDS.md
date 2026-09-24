# DNAi model cards

DNAi Systems. Revision of 24 September 2026, the launch revision for 1 October 2026. Supersedes the internal card of 14 September.

Asha is an AI system in the HealthBench Professional paper's sense: a model plus a harness. Every tier below is the same neurosymbolic stack (retrieval, falsification, safety gating, composition) wrapped around vendor language models. No tier uses a fine-tuned model. Every gain over a bare backbone reported here is architectural and is measured against that backbone on the same items, under the same grader.

Numbers carry their source, set size and grader. Where a number is not on the public register at [dnai.systems/benchmarks](https://dnai.systems/benchmarks) it is marked as such. The register is canonical; if this card and the register ever disagree, the register is right and this card is stale.

## 1. What every tier shares

**Knowledge.** One curated corpus, retrieved through the Knowledge Integration Layer (KIL): about 350 knowledge collections holding 144M+ vectors (audit of 11 September 2026): PubMed and PMC full text, OpenAlex, drug labels (DailyMed, FDA, FAERS), clinical references and guidelines, medical coding, textbooks, and domain corpora for finance, law, nutrition and fitness, with recency lanes refreshed on schedule. Per-user memory is stored separately and is never a knowledge source. A contamination probe on 200 of the 5,000 HealthBench items found no retrievable benchmark content in the collections Asha searches (nearest-neighbour cosine below 0.92 throughout).

**Backbone models (frozen 20 September 2026).** Panel agents run on Claude Sonnet 5 (task gravity below 0.8) and Claude Opus 5 (0.8 and above). The Apex-J composer is GPT-6 Astra with a 4,096-token budget and the concise style. Gemini serves PHI-adjacent pipelines under the Vertex AI BAA.

**Safety, all tiers.** Jailbreak detection; a contract validator on every agent output; a capitulation detector with one restraint regeneration; crisis resources surfaced whenever risk language appears (988 in the US), bypassing quotas; an evidence gate; every answer written to a ledger and every API call to an audit log. Refusals are rare by design: Asha answers with safety framing rather than declining. Across the 5,000-item HealthBench run, 525 clinician prompts, and 500 study-sample items reported below, the refusal count is zero.

**Routing.** Task gravity, a stakes score computed per query, chooses the tier on the consumer surfaces: Base below 0.70, Mid from 0.70 to 0.88, Apex at 0.88 and above with a daily cap. API customer keys run Base by default; Apex is an explicit, asynchronous, per-answer product.

**Shared limitations.** Deep paths take 40 to 150 seconds. There is no automatic provider failover today (a provider outage on 22 September 2026 was handled by a manual switch to the Vertex path). Knowledge recency depends on the refresh lanes. Rubric-graded benchmarks move several points between graders, so every headline number is reported with its grader and, where measured, two sensitivity graders.

## 2. Asha Base

| Field | Value |
|---|---|
| Pipeline id | P2 |
| Architecture | One KIL-grounded pass: retrieval across the admitted collections, evidence assembled into the prompt, one backbone call, safety gates, ledger write |
| Backbone | Claude Sonnet 5 (gravity < 0.8) or Claude Opus 5 (gravity >= 0.8) |
| Where it runs | Every consumer query below gravity 0.70; the API default for customer keys; the panel members inside Apex-J |
| Intended use | Everyday health questions, medication facts, triage guidance, documentation help; high volume, low latency |
| Not for | Complex multi-morbidity consults (the cascade escalates); research syntheses that need the panel |
| Latency | about 20 to 30 s typical on the API; seconds to first token on the stream path |
| HealthBench Standard (5,000, gpt-4.1) | 44.1 (June 2026 build; independently recomputed 44.06 by Airpixels Innovations LLP, 10 Sep 2026). Kept as lineage on the register |
| HealthBench Hard (1,000) | 28.4 (June 2026 build; recomputed 28.35) |
| MedQA (locked 1,273) | see the register row `medqa-usmle-locked` for the artifact score and the fresh re-runs |
| Psychosis Bench | deployed Asha fresh run by the independent validator 96.9% SIS (93 of 96 turns) |
| Known limitations | Single-model answer, so no cross-family check |

## 3. Asha Mid

| Field | Value |
|---|---|
| Pipeline id | P5 (deep-mode ensemble) |
| Architecture | Three KIL-grounded drafts in parallel from different model families, quorum of two, then a composer merges under a union-of-correct, falsify-before-include discipline; degrades to the best single draft if the merge times out |
| Where it runs | Consumer stream path, gravity 0.70 to 0.88 |
| Intended use | Higher-stakes single-question consults where a second model family adds a check without the panel's cost |
| Latency | roughly 40 to 50 s design envelope |
| HealthBench Standard (5,000, gpt-4.1) | 60.6 (June 2026 build; recomputed 60.59). Kept as lineage on the register |
| HealthBench Hard (1,000; 898 scored) | 37.9 (recomputed 37.94); +9.7 pp over Base, paired, p about 1e-19 |
| Known limitations | The least-measured tier: not run on HealthBench Professional, MedHELM or the Psychosis Bench as a separate arm |

## 4. Asha Apex (P6): the June 2026 build, lineage

| Field | Value |
|---|---|
| Pipeline id | P6, composer Claude Opus 4.8, FENG on |
| Architecture | Eleven specialist agents (medicine, research, science, finance, law, nutrition, fitness, practice management, growth, support, platform), each drafting with its own retrieval; FENG falsifies extracted claims against the corpus; a domain-expert composer merges; waits for all agents |
| Status | Replaced as the served Apex tier by Apex-J on 20 September 2026. Its June numbers stay on the register as lineage comparators |
| HealthBench Hard (1,000, gpt-4.1) | 44.8 [43.0, 46.6] (June 2026); re-graded with today's gpt-4.1 on the identical June answers on 22 Sep 2026: 44.8 (grader stable) |
| HealthBench, Vishwanath 500 | 68.4 under the study's published three-judge panel (Claude Opus 4.6, Gemini 3.1 Pro Preview, GPT-5.2; graded 23 Sep 2026 in the study's own pipeline on the June answers). Earlier figures quoted for this set (72.6 under gpt-4.1 single) were a different grader from the published tools' and are retired |
| MedHELM efficient (n = 30 per scenario) | see the register appendix; small samples, never headline claims |
| Psychosis Bench | SIS 97.9% (30 June 2026) |
| Known limitations | Waited for the slowest agent; the longest answers of any tier (about 4,600 characters median on the 500) |

## 5. Asha Apex-J (frozen 20 September 2026): the served Apex tier at launch

| Field | Value |
|---|---|
| Pipeline id | P6-J. Freeze tag `freeze-2026-09-20`. Process fingerprint of the measured build `edd4f69f9a9bd6d2` |
| Architecture | The Apex panel rebuilt as jiva agents: quorum kickoff (7 of 11 with a straggler grace) and retries; the clinician agent's draft always carried into composition with its safety check-in; conversation-carried domain guardianship; a grounding check on the composed answer; a composer budget. Composer GPT-6 Astra, 4,096 tokens, concise style. FENG on, KIL on |
| Where it runs | The Apex tier of the production cascade since 20 September 2026 (web stream path, non-stream `/api/query`, A2A `message:send` at depth auto, and the OpenAI-compatible model `asha-apex`) |
| Intended use | Clinician-facing consults, documentation, research synthesis: the tier DNAi publishes |
| Not for | Real-time use: 60 to 150 s deep path |
| Latency | mean about 80 s, p90 about 110 s on the bench lane |
| **HealthBench Standard (5,000, gpt-4.1)** | **60.7 [59.8, 61.5]** vs bare GPT-6 Astra 52.7 on the same items: +8.0 pp, p = 7e-110, wins/losses/ties 2,618 / 1,162 / 1,220. Sensitivity graders: GPT-5.4 55.2 vs 48.1 (+7.1); Claude Opus 4.8 65.9 vs 57.8 (+8.4) |
| **HealthBench Hard (1,000, gpt-4.1)** | **42.0 [40.1, 43.7]** vs bare GPT-6 Astra 29.4: +12.6 pp, p = 4e-37. GPT-5.4 37.3 vs 24.9; Opus 4.8 50.3 vs 35.7 |
| **HealthBench, Vishwanath 500 (study pipeline, three-judge panel)** | **63.8** vs OpenEvidence 62.6 and UpToDate Expert AI 61.3 as published by the study under the same panel; bare GPT-6 Astra 54.9 under the same panel. Every one of the 5,782 criteria received three clean votes |
| HealthBench Professional (525) | see the register row; the ladder that selected this configuration ran on this set under GPT-5.4 (official for that paper) with Opus 4.8 as sensitivity |
| Psychosis Bench | frozen configuration: see the register row `psychosis-bench-sis` |
| Refusals | 0 on the 5,000; 0 on the 500; 0 on the 525 |
| **Pre-registered harm test** | Harm proxy = share of negative-point rubric criteria the answer triggers, vs bare GPT-6 Astra on the same items, bound +2.0 points. Standard: **+2.8 under gpt-4.1 (not met)**, −0.3 under GPT-5.4, −0.4 under Opus 4.8. Hard: +1.6, −3.2, −4.1. The gpt-4.1 excess is concentrated in length and over-detail criteria ("excessively long", "beyond a brief list", "assumes without asking"); factual-error criteria account for 59 of the 1,851 extra hits; on severe criteria (8 points or worse) Apex-J trips fewer than the bare model under GPT-5.4 and Opus 4.8 and 81 more under gpt-4.1. Reported on the register row with the number |
| Where it wins and loses (Standard, gpt-4.1, vs bare Astra) | Wins every theme: global health +12.3, context seeking +11.1, hedging +9.0, health data tasks +7.4, communication +4.7, emergency referrals +4.3, complex responses +1.1. Axes: completeness +13.9, accuracy +6.6, context awareness +3.6, instruction following +1.7, communication quality −8.0. Median answer 2,725 characters vs 1,400 |
| Deployed-code identity checks | The served code was re-run on the 500 twice after the freeze because other changes landed on the shared engine: 23 Sep, panel 63.7 vs the frozen run's 63.8, gpt-4.1 61.4 vs 61.6 (p = 0.83); 24 Sep, in progress at this revision. Both are on the register as "Also measured" |
| Style check | The default composer style on the same code and items scored lower than concise on every grader (panel 62.2 vs 63.7; gpt-4.1 58.3 vs 61.4, p = 0.0009) and produced shorter answers. Concise stays |
| Lineage, stated plainly | On raw rubric scoring the frozen build is below the June P6 build: 42.0 vs 44.8 on Hard under the same grader, 63.8 vs 68.4 on the 500 under the same panel. The June build's fuller answers (about 4,600 vs 2,700 characters) earn completeness points that the concise style gives up. That gap is the post-launch target |
| Known limitations | Communication-quality axis below the bare backbone; the gpt-4.1 harm-proxy miss above; deep-path latency; the corpus recency lanes |
| External validation | The June builds were validated by Airpixels Innovations LLP (Package 1, signed 10 Sep 2026). The frozen Apex-J's own external validation is scheduled after launch; every per-item artifact needed for it is in this repository |

## 6. Comparison chart (launch revision)

| Dimension | Base | Mid | Apex (P6, June) | Apex-J (frozen, served) |
|---|---|---|---|---|
| Model families per answer | 1 | 3 + composer | 11 agents + composer | 11 agents + composer |
| Retrieval | KIL, 1 pass | KIL, 3 grounded drafts | KIL per agent + FENG | KIL per agent + FENG |
| Typical / p90 latency | ~25 s / ~30 s | ~45 s / ~50 s | 81 s / 124 s | ~80 s / ~110 s |
| HealthBench Standard 5,000 (gpt-4.1) | 44.1 (June) | 60.6 (June) | not run on 5,000 | **60.7** |
| HealthBench Hard 1,000 (gpt-4.1) | 28.4 (June) | 37.9 (June) | 44.8 (June) | **42.0** |
| Vishwanath 500, published panel | not run | not run | 68.4 | **63.8** (OpenEvidence 62.6, UpToDate 61.3) |
| Refusals on clinician prompts | rare | rare | 0 | 0 |
| Served on 1 Oct 2026 | yes (API default, cascade low band) | yes (cascade mid band) | no | yes (cascade high band, `asha-apex`) |

## 7. API model names

| API name | Tier | Notes |
|---|---|---|
| `asha-base` | Base | default for customer keys |
| `asha-mid` | Mid | cascade band 0.70 to 0.88 |
| `asha-apex` | Apex-J | asynchronous; explicit per-answer product |

The other DNAi agents (Harley, Artha, Sage, Polymath, Lyra, Leo, Mira, Ren, Arohi, Ray) are reachable over the A2A protocol and documented in their own public repositories under [github.com/EndlessRay](https://github.com/EndlessRay).

## 8. Sources

Public benchmark register: [dnai.systems/benchmarks](https://dnai.systems/benchmarks) (JSON at `/benchmarks.json`, API at `/api/benchmarks`). Per-item artifacts for the 5,000-item run, the 500-item panel grades, the identity and style checks: [`benchmarks/healthbench-5000-2026-09-20/`](benchmarks/healthbench-5000-2026-09-20/). June 2026 artifacts: [asha-healthbench-2026-06-26](https://github.com/EndlessRay/asha-healthbench-2026-06-26). MedQA, Psychosis Bench, META_CORRECT: [asha-bench-public](https://github.com/EndlessRay/asha-bench-public). Vishwanath et al., Nature Medicine 2026, and the study's public pipeline: [nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks). HealthBench: Arora et al., arXiv:2505.08775.
