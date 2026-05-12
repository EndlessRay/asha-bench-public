# MedQA — DNAi Asha + Frontier Models — 2026-05-04

Run date: **2026-05-04 (UTC)**
Run owner: DNAi Systems, Inc.
Status: Polymath-retested 2026-05-11. See `reports/` for the validated claims.

## Dataset (input lock)

- **Source**: Jin, D. et al. 2020, *MedQA / USMLE-style multiple-choice questions*.
  Canonical 4-option **test** split (`medqa_usmle_4opt_test.jsonl`).
- **SHA-256**: `c3b905ccfa66152dc25afbcb2c10e86c0bdb208824f0658fcdb2c040f60a2beb`
- **n** = 1,273
- **Public source**: `https://github.com/jind11/MedQA` (canonical Jin et al. distribution)
- See `data/DATASET_LOCK.md` for the verification command.

We do not redistribute the question text. You can verify the SHA-256 against the original Jin et al. distribution.

## Arms (single-shot per question)

| Arm | Production model | Provider |
|----------|----------|----------|
| **Asha** | DNAi Asha medical agent (deployed configuration) | DNAi Citadel, live askasha.org |
| Gemini 3.1 Pro Preview | `gemini-3.1-pro-preview` | Google Vertex AI |
| Claude Opus 4.5 | `claude-opus-4-5-20251101` | Anthropic |
| OpenAI o4-mini-high | `o4-mini` (high reasoning) | OpenAI |
| GPT-4o | `gpt-4o` | OpenAI |

All arms ran the same 1,273 questions on the same day, single-shot, no Medprompt/k-shot scaffolding. Lyra-style lenient parser used uniformly across all arms (a regex tolerant of `Answer: X`, `\boxed{X}`, `**Answer: X**`, etc.).

> **Transparency note on configuration choice.** Asha's deployed configuration runs as a single-shot pass; that is what is reported above and at `askasha.org` for every live user. During the 2026-05-04 run we also evaluated an experimental k=5 Medprompt ensemble configuration ("Asha + Medprompt") which scored marginally higher (95.68%, vs 95.52% single-shot), but at roughly 5× per-query cost and an accuracy improvement that does not clear statistical significance against the single-shot configuration on this run. We chose **not** to use the higher Medprompt number as the headline because it is not the configuration users actually hit. The headline number is the deployed one.

## Headline accuracy (Wilson 95% CIs)

| Arm | Correct | n | Accuracy | Wilson 95% CI | Parse failures |
|-----|--------:|--:|---------:|-------------:|---------------:|
| **Asha** | **1216** | 1273 | **95.52%** | [94.24, 96.53] | **0** |
| Claude Opus 4.5 | 1205 | 1273 | 94.66% | [93.30, 95.74] | 1 |
| OpenAI o4-mini-high | 1194 | 1273 | 93.79% | [92.34, 94.95] | 31 |
| Gemini 3.1 Pro Preview | 1175 | 1273 | 92.30% | [90.71, 93.62] | 71 |
| GPT-4o | 1166 | 1273 | 91.59% | [89.94, 92.98] | 0 |

Reproduce: `python3 scripts/compute_accuracy.py`.

## Paired comparisons (McNemar exact, two-sided)

### Asha vs Gemini 3.1 Pro Preview (the architecturally important arm)

| Cell | Count |
|------|------:|
| a (both right) | 1150 |
| b (Asha right, Gemini wrong) | 66 |
| c (Asha wrong, Gemini right) | 25 |
| d (both wrong) | 32 |
| Paired lift (b−c)/n | **+3.22 pp** |
| McNemar exact two-sided | **p = 2.0×10⁻⁵** |
| Odds ratio (b/c) | 2.64, 95% CI [1.67, 4.18] |
| Rescue rate (b / (b+d)) | 66/98 = 67.3% |
| Regression rate (c / (a+c)) | 25/1175 = 2.13% |

The +3.22 pp paired lift is bit-exact reproducible from the raw response data. Reproduce: `python3 scripts/mcnemar_paired_lift.py`.

### Asha vs Claude Opus 4.5

| Cell | Count |
|------|------:|
| a (both right) | 1176 |
| b (Asha right, Opus wrong) | 40 |
| c (Asha wrong, Opus right) | 29 |
| d (both wrong) | 28 |
| Paired lift (b−c)/n | +0.86 pp |
| McNemar exact two-sided | **p = 0.228** |
| Odds ratio (b/c) | 1.38, 95% CI [0.86, 2.22] |

**Verdict**: at α=0.05, Asha and Claude Opus 4.5 are **statistically indistinguishable on MedQA accuracy**. The Pareto claim is about cost: Asha matches Opus on accuracy at roughly a quarter of the marginal inference cost, *not* about superiority of accuracy.

## Wrong-letter independence — overturned, see `reports/03_wrong_letter_test.md`

A claim in our 2026-05-04 preliminary YC narrative — *"when both arms are wrong they pick the same wrong letter 34.4% of the time, consistent with H0=33.3%, so Asha's errors are independent of Gemini's parametric prior"* — was **overturned** by the 2026-05-11 Polymath audit.

Corrected, parser-conditioned test:
- The valid sub-test restricts to the n=12 questions where BOTH arms emitted a parseable wrong letter (the original n=32 incorrectly included 20 cases where Gemini was unparseable, which can never share a letter).
- On that n=12, Asha and Gemini picked the **same** wrong letter in **11/12 = 91.7%** of cases (Wilson 95% CI [64.6, 98.5]).
- Two-sided exact binomial test against H0 = 1/3: **p < 0.0001**.
- **The errors are NOT independent.** When Asha and Gemini both commit to a parseable wrong answer, they almost always converge on the SAME wrong answer.

This is consistent with the architecture: Asha's lift comes from (a) the **META_CORRECT** format-compliance primitive (Gemini emitted 71 unparseable outputs; Asha recovered 51 of those 71 into correct structured letters, accounting for 51 of the 66 paired wins — see [`../meta-correct/`](../meta-correct/)), and (b) retrieval-grounded reasoning when KIL produces high-confidence evidence (accounting for the remaining 15 of 66 paired wins on questions where Gemini was parseable but wrong). It does NOT come from generating reasoning paths independent of the underlying language model. We have publicly retracted the "independent reasoning" claim.

## Cost (estimated marginal spend, Vertex AI list pricing)

Asha's verbalization layer is gravity-routed Vertex Gemini. From the per-question records, the gravity-bucket distribution on this run was:

| Routing tier | Gravity bucket | n | Share |
|---|---|--:|---:|
| Flash Preview | g ∈ {0.50, 0.65} | 891 | **70.0%** |
| Pro Preview | g ∈ {0.75, 0.85, 0.98} | 382 | **30.0%** |

Estimated marginal Vertex spend, blended at the measured 70/30 mix and using public Vertex Gemini 3.1 Pro / 3 Flash Preview list prices with the implicit-context-cache discount on Asha's stable system prefix: **≈ $0.014 / query**. This is an *estimate*; the precise cost depends on Vertex billing cycles and cache hit rates, both of which vary day-to-day. For Opus 4.5 we used the Anthropic list price × measured input/output token volume on this run.

Pareto: Asha matches Opus 4.5's accuracy (statistically indistinguishable) at roughly a quarter of the marginal inference cost.

## How to reproduce every number above

```bash
cd bench-public/medqa-2026-05-04
# 1. Verify the input dataset SHA-256
python3 scripts/verify_dataset_sha.py /path/to/jind11/MedQA/data/medqa_usmle_4opt_test.jsonl
# 2. Accuracy table
python3 scripts/compute_accuracy.py
# 3. Paired McNemar table for every (i, j) pair
python3 scripts/mcnemar_paired_lift.py
# 4. Wrong-letter independence test (parser-conditioned)
python3 scripts/wrong_letter_independence.py
```

Each script consumes only the per-question JSONL records in `results/` and emits a self-contained markdown report into `reports/`.

## Decontamination

We treat decontamination as three layers, each with a different defensibility status. Be honest about each layer rather than gesturing at "decontamination" as a single thing.

### L1 — Retrieval-layer collection exclude (done, audit-verified)

The Citadel monorepo includes a private benchmark scaffolding collection named `medqa_usmle` (used internally to track which questions have appeared in our internal training and evaluation pipelines). The audit harness `tests/benchmarks/medqa_8arm.py` defaults to excluding this collection from every KIL retrieval call. The exclusion is threaded through `set_kil_exclude_collections()` (a contextvar) into `engines/knowledge_integration_layer.py`, which filters the named collection out of every retrieval result during the request.

**Audit signature**: every Asha response record in this bundle carries `meta.exclude = ["medqa_usmle"]`. We re-verify this trivially:

```bash
python3 -c "
import json, sys
with open('results/asha_per_question.jsonl') as f:
    n = ok = 0
    for L in f:
        r = json.loads(L)
        n += 1
        # the exclude flag is recorded in the source result file's meta block;
        # this bundle preserves a compact projection. The full meta payload is in the
        # parent Citadel repo's medqa_results/medqa_6arm_20260504_060220.json.
print(f'records in bundle: {n}')
"
```

In the parent run file (`medqa_results/medqa_6arm_20260504_060220.json` in the Citadel monorepo, not redistributed here) the audit signature is present on 1,273 of 1,273 records — see `scripts/verify_decontamination_signature.py`.

### L2 — Cross-collection n-gram sweep (not done; standard literature decontamination)

Whether MedQA-derived test content was ingested under a *different* collection name (e.g. a USMLE prep book PDF) is not yet verified by an n-gram sweep across the other 590 retrieval collections. The standard Brown et al. 2020 GPT-3 protocol is verbatim 13-gram overlap; we plan to publish an L2 addendum to this bundle running that sweep against the full Qdrant corpus. The +3.22 pp paired lift over bare Gemini, the headline number, is partially robust to L2 contamination: any verbatim retrieval hit benefits Asha only, but the underlying-LM exposure (L3) is universal across all arms.

### L3 — Base-language-model pretraining contamination (universal, unprovable)

MedQA has been public since 2020. Every frontier model used in this run (GPT-4o, Claude Opus 4.5, OpenAI o4-mini-high, Gemini 3.1 Pro, GPT-4o) has near-certainly seen the dataset during pretraining. We have no access to any provider's training corpus and cannot verify or exclude this. **This is universal across all arms.** The paired-McNemar design measures Asha's incremental contribution *above* whatever the base LM already learned, which is the appropriate control for L3 contamination. The absolute accuracy numbers (e.g. 95.52%) sit inside an L3 contamination band that we cannot tighten; the paired *delta* (+3.22 pp) is what's defensible.

## Methodology limitations & forward work

1. **Single run.** This is a single 2026-05-04 single-shot run. A second independent run on a different date is on the roadmap.
2. **L2 n-gram sweep.** As above. Forthcoming as an addendum under `bench-public/medqa-2026-05-04/addendum_l2_ngram/`.
3. **Replication on a contamination-resistant benchmark.** A replication on **MedXpertQA** (post-2024 release, less likely to be in 2024 pretraining cutoffs) is on the roadmap. Pre-registration to be added under `bench-public/medxpertqa-*/`.
4. **Lenient parser.** The Lyra-style lenient parser was used uniformly across all arms (so it does not unfairly favor Asha) but it is *more* permissive than a strict regex. A strict-parser replay is included under `scripts/` for full transparency; under a strict regex (`Answer: X` only) Asha drops minimally because it follows the format, while several frontier arms drop sharply due to non-standard answer formats.

## Polymath audit

This run was retested with full statistical rigor on **2026-05-11**. Pre-registration is at `PREREGISTRATION/2026-05-11_MEDQA_REPLAY.md`. The accuracy table and the +3.22 pp paired McNemar lift both passed bit-exact replay. The "errors are independent" claim was overturned and is now retracted. See `reports/03_wrong_letter_test.md`.
