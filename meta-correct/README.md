# META_CORRECT — the architectural primitive (Chapter 2)

A deterministic, evidence-grounded, cryptographically-auditable post-emission corrector for structured language-model outputs in regulated domains. Live under DNAi's medical agent Asha at [askasha.org](https://askasha.org). US Provisional **397222-7002P1** filed 2026-05-01; continuation-in-part draft on file with counsel.

The full specification is held by counsel and not published here. This chapter documents the **empirical effect** by cross-referencing the two flanking benchmark chapters in this same repository.

## Why this chapter exists

Chapters 1 and 3 each report a measurable lift Asha shows over the bare language model it ultimately speaks through:

| Bench | Failure mode it measures | Lift Asha shows over bare Gemini |
|---|---|---|
| Chapter 1 — MedQA | **Structural**: does the LM produce a parseable letter answer? | **+3.22 pp** paired McNemar; **51 of Gemini's 71 parse-failures rescued** to a correct letter |
| Chapter 3 — Psychosis-bench | **Semantic safety**: does the LM amplify a clinically dangerous belief, or enable a clinically dangerous act? | DCS, HES, SIS gaps quantified — see [`../psychosis-bench-2026-05-11/`](../psychosis-bench-2026-05-11/) |

Both lifts come from the same architectural primitive: a deterministic post-emission corrector that operates on the LM's output **after** generation, **before** the reply is shown to the user. In Chapter 1 the corrector enforces format compliance (parser-passable structured letter). In Chapter 3 the corrector enforces semantic-safety constraints (refusal of delusion-confirming content, mandatory intervention on harm-enabling content). Same primitive, two regulated-domain failure modes.

## What is auditable in this repository

Without the patent spec, the artifacts in the flanking chapters are still sufficient for an external party to verify that META_CORRECT *empirically* operates on the bare-LM output:

1. **MedQA parse-failure table** ([`../medqa-2026-05-04/`](../medqa-2026-05-04/))
   - Asha emitted **0 parse failures in 1,273 questions** (0.00%).
   - Bare Gemini 3.1 Pro Preview, on the *same* questions on the *same* day, emitted **71 parse failures in 1,273** (5.58%).
   - Of the 66 paired wins where Asha was correct and Gemini was wrong (Wilson-significant McNemar lift), **51 are accounted for by rescued parse-failures** — `medqa-2026-05-04/results/medqa_5arm_20260503_235519.json`, filterable in five lines of Python.
   - Asha emits 0 / 1,273 even though *its own verbalization layer is Gemini Flash + Pro Preview routed*. The corrector is operating after the verbalization layer.
2. **Psychosis-bench paired excerpts** ([`../psychosis-bench-2026-05-11/reports/03_paired_excerpts.md`](../psychosis-bench-2026-05-11/reports/03_paired_excerpts.md))
   - Four scenario turns where the user is in active delusion confirmation, the bare Gemini-Flash arm amplifies, and the Asha arm refuses + grounds + offers concrete clinical resources.
   - Every paired excerpt has the full markdown of both responses verbatim from `per_turn_judge_a.jsonl`. An external reviewer can recompute the judge labels themselves with the upstream prompts and confirm the score disparity is not a judge artifact.

## What is NOT in this repository

* The patent specification (US Provisional 397222-7002P1) — held by counsel.
* The deterministic corrector source code — internal to Citadel.
* Any claim that META_CORRECT *prevents* a failure the underlying LM would not have made. The claim is strictly that META_CORRECT *catches* failures the underlying LM **does** make in these benchmarks. The structural and semantic failure modes the corrector catches are observable in the bare-LM column of the paired tables in Chapters 1 and 3.

## How a reviewer verifies the lift is "the architecture" and not "a better LM"

Both Chapter 1 and Chapter 3 hold the underlying LM family constant. In Chapter 1, the McNemar comparison is Asha (Gemini-Flash + Pro Preview routed, gravity-aware) vs bare Gemini 3.1 Pro Preview — and the paired lift is +3.22 pp. In Chapter 3, the comparison is Asha (whose verbalization layer is ~70% `gemini-2.5-flash` text) vs bare `gemini-2.5-flash`. Where the language model is functionally identical between arms, the only remaining variable is the META_CORRECT layer and the surrounding KIL retrieval and Resolve(P) cognition. The paired-McNemar / scenario-paired-bootstrap analyses isolate the architectural contribution.

## Contact

For patent and licensing discussions: counsel of record (Saul Ewing). For technical questions about the *empirical* findings: [founders@dnai.systems](mailto:founders@dnai.systems).
