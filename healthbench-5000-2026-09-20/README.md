# HealthBench, 5,000 items: the frozen Asha Apex-J vs its bare backbone

Per-item artifacts for the launch measurement of Asha Apex-J (frozen 20 September 2026) on the full OpenAI HealthBench set (5,000 conversations; Hard 1,000 and the Vishwanath et al. 500-item sample are exact subsets), plus the study-pipeline panel grades of the 500, the deployed-code identity checks and the composer-style check. Everything the register rows `healthbench-standard`, `healthbench-hard-apex` and `healthbench-500-independent` at [dnai.systems/benchmarks](https://dnai.systems/benchmarks) cite is here, with SHA-256 in `MANIFEST.json`.

## Method

- **Dataset.** OpenAI HealthBench `2025-05-07-06-14-12_oss_eval.jsonl` (5,000 items, SHA-256 `e99dd3c6372c10d6fcc5e385c5fae69d0dd40392dae56836ef9493ae324ecd2f`), unmodified. Hard: `hard_2025-05-08-21-00-10.jsonl` (1,000 items, an exact subset). The Vishwanath 500: the study's seed-62 sample, `vishwanath_seed62_500_items.jsonl` in this folder (500 of the 5,000, matched by text and id).
- **Arms.** `asha-apex-j-frozen`: the served Apex tier, one trial, every item answered with the full conversation, on the bench lane pinned to process fingerprint `edd4f69f9a9bd6d2` for the whole run. `bare-gpt-6-astra`: GPT-6 Astra through the vendor API, no system prompt, no tools, no retrieval, highest effort, the same 5,000 items. The bare arm is the composer backbone without the Asha layer; the paired difference is the architecture.
- **Grading.** Three graders, each scoring every rubric criterion of every item for both arms: gpt-4.1 (the official HealthBench grader), GPT-5.4 at low reasoning, Claude Opus 4.8. The score of record is gpt-4.1. Grader calls that failed (vendor errors, parse failures) are stored with an `Error`/`Parse failed` explanation and are excluded from scoring, never counted as unmet; the counts are in the readouts. The grading was interrupted by a vendor credit outage on 22 September and resumed; rows that carried error codes were discarded and re-graded, so no partial row is counted.
- **Score.** HealthBench convention: per item, points earned divided by positive points possible (negative-point criteria subtract when triggered); the benchmark score is the mean over items clipped to [0, 1]; theme, axis and physician-category scores are the per-item tag scores averaged the same way. Bootstrap 95% intervals (4,000 resamples). Paired differences on shared items with a two-sided t-test and an exact sign test.
- **Harm proxy.** Share of negative-point criteria triggered, per grader. The pre-registered test (within +2.0 points of the bare arm on the 5,000) is reported per grader in the readouts and on the register rows, pass or miss.
- **Panel grades of the 500.** The same 500 answers (nothing regenerated) scored in the study's own public pipeline ([nyuolab/clinical-llm-benchmarks](https://github.com/nyuolab/clinical-llm-benchmarks), `evaluation_pipeline.py healthbench --panel-models`) with the published three-judge configuration: Claude Opus 4.6, Gemini 3.1 Pro Preview, GPT-5.2, majority per criterion, points achieved over points possible. The run refused to start unless all three judges answered a probe, so the panel never degraded to two votes; the outputs record every judge's vote per criterion.
- **Identity and style checks.** Because other work landed on the shared engine after the freeze, the served code was re-run on the 500 (concise style) and compared with the frozen run's answers; the default composer style was run on the same code for comparison. Same lane, same items, same three graders and the same panel.

## Files

| Path | Contents |
|---|---|
| `asha-apex-j-frozen/completions.jsonl.gz` | 5,000 rows: `prompt_id`, `prompt` (the conversation), `completion`, `rubrics`, `example_tags`, `draft_count`, `contributing_agents`, and a reduced `endlessray_metadata` (pipeline id, process fingerprint, composer and agent model names, latency). Internal instrumentation fields are removed |
| `asha-apex-j-frozen/graded_{gpt_4_1,gpt_5_4,claude_opus_4_8}.jsonl.gz` | per-item grades: `score`, `metrics` (per-tag scores), `rubric_grades` (criterion, points, met, grader explanation) |
| `asha-apex-j-frozen/run_manifest.json` | dataset SHA-256, item count, graders, composer arguments, the pin (fingerprint, provider routing, quorum, culture charter hash, KIL fingerprint), repository commit |
| `bare-gpt-6-astra/` | the same layout for the bare backbone arm |
| `identity-check-2026-09-23-concise/`, `style-check-2026-09-23-default/` | the same layout for the two 500-item checks |
| `readouts/official_readout_hb5000_{standard,hard,seed62}.json` | the full readout per set: per grader, both arms, bootstrap intervals, paired tests, harm proxy, refusals, per-tag tables, provenance |
| `readouts/decision_readout_hb500_*.json` | identity and style readouts (same schema) |
| `readouts/hb500_panel_summary.json` | panel scores and vote-integrity counts for the register arms |
| `readouts/june_p6_hard_regraded_gpt41_2026-09-22.jsonl.gz` | the June 2026 Apex (P6) Hard answers re-graded by today's gpt-4.1 (44.8, identical to June: the grader is stable) |
| `vishwanath-500-panel/panel_*.json.gz` | study-pipeline outputs with every judge's vote per criterion: frozen Apex-J, bare GPT-6 Astra, the June 2026 Apex (P6) answers, the identity check, the style check |
| `vishwanath_seed62_500_items.jsonl` | the 500 items |
| `MANIFEST.json` | SHA-256 and size of every file above |

## Headline numbers (gpt-4.1 unless stated)

| Set | Asha Apex-J | bare GPT-6 Astra | Paired delta | Harm proxy delta |
|---|---|---|---|---|
| Standard 5,000 | 60.7 [59.8, 61.5] | 52.7 | +8.0, p = 7e-110 | +2.8 (GPT-5.4 −0.3, Opus 4.8 −0.4) |
| Hard 1,000 | 42.0 [40.1, 43.7] | 29.4 | +12.6, p = 4e-37 | +1.6 (−3.2, −4.1) |
| Vishwanath 500, three-judge panel | 63.8 | 54.9 | +8.9 | n/a |
| Vishwanath 500, published tools, same panel | OpenEvidence 62.6, UpToDate Expert AI 61.3 | | | |
| June 2026 Apex (P6), same panel | 68.4 | | | |

Refusals: zero in every arm.

## Re-grading

Any item can be re-graded from `completions.jsonl.gz` with the official HealthBench grader (OpenAI simple-evals, gpt-4.1) or with the study pipeline above. The `metrics` field in each graded row follows the simple-evals tag convention, so theme and axis tables reproduce with a group-by.

## Cite

DNAi Systems, "Asha Apex-J on HealthBench, 5,000 items, frozen 20 September 2026", artifact set of 24 September 2026, github.com/EndlessRay/asha-benchmarks.
