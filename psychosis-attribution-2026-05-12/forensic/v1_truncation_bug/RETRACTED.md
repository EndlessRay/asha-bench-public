# RETRACTED — BENCH6 v1 run (max_output_tokens truncation)

**Status**: RETRACTED. Results are artifacts. Do not use.
**Retracted by**: DNAi audit team, 2026-05-12, before any external publication.
**Replacement**: `results/per_turn_bench6_pro.jsonl` (v2, clean run).

## What happened

A v1 run of the BENCH6 `raw_gemini_pro` arm completed on 2026-05-12 and
produced 191/192 empty model responses (`text=""`,
`FinishReason.MAX_TOKENS`). The v1 arm code inherited a
`max_output_tokens=1024` cap from `AshaGeminiOfflineArm`.
`gemini-2.5-pro` is a **thinking model** — its hidden chain-of-thought
tokens count against `max_output_tokens`. At multi-turn adversarial
prompt lengths, the 1024-token budget was exhausted entirely by thinking,
leaving zero tokens for the visible response.

The judge (`gpt-4o-mini`) then scored empty strings, producing:
- Artifactual DCS = 1.139 (a judge-on-empty-string baseline)
- Artifactual HES = 0.792
- Artifactual SIS = 5/96 = 5.2% (judge inconsistently scored some empty
  strings as SIS=1)

## How it was caught

Quality-check before reporting: `sum(1 for r in rows if r['model_response'] == '')` returned 191. Direct verification confirmed `FinishReason.MAX_TOKENS` with `candidates_token_count=None` and `text=""`.

## Fix

`RawGeminiProArm` now mirrors `GeminiFlashArm` exactly — no
`GenerateContentConfig` block, no `max_output_tokens` cap. SDK default
(~8192 output tokens) accommodates the thinking budget plus a real
response. Verified: same adversarial prompt returns 2,733-character text
with `FinishReason.STOP` after the fix.

Fix commit: `26e3e27b` (`fix(bench6): drop max_output_tokens cap`).

## Relation to earlier known bug

The same bug affected the `gemini_flash` arm in the internal
`_full_run2_haiku_max_tokens_fixed` BENCH2 archive (192/192 empty
responses), discovered during the Proviso 1 audit on 2026-05-12. That
archive is not used as a control in any public-facing result. The Chapter
3 control numbers (DCS=1.215, SIS=30.2% for bare Flash) come from the
REDO run (`bench2_psychosis_dualjudge_REDO_LOCAL`) which has 0 empty
responses on both arms.

## Preserved files

The v1 artifact data is preserved here for transparency:
- `v1_per_turn.jsonl` — 192 rows, 191 with `model_response: ""`
- `v1_aggregate.json` — artifact aggregate statistics
