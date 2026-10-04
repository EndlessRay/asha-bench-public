# PWS-SafeBench v1.0 (2026-10-03)

Pre-registered, multi-model adversarial safety benchmark for Prader-Willi syndrome. Companion to the FPWR 2026 Research Symposium oral and the manuscript in `Docs/preprint/pws-ai-safety-2026-10/`.

- `PREREGISTRATION.md` (locked at commit `39911be9`, 2026-10-03 15:46 EDT) and `PREREGISTRATION_AMENDMENT_1.md` (token ceilings, before first query)
- `data/pws_safebench_v1.0.json` item bank, SHA-256 `e2312422a41bec58d911ef857d81d6004811628a74a6b52c41b2708d8e2728cf`; `data/ITEM_RATIFICATION.md`
- `scripts/`: `build_items.py`, `verify_item_sources.py`, `run_pws_safebench.py`, `judge_pws_safebench.py`, `citation_verify.py`, `stats_pws_safebench.py`, `make_study2_sample.py`
- `results/`: `responses.jsonl` (384), `judgments.jsonl` (768), `citations.jsonl`, `citation_adjudication.json`, `stats.json`, `RESULTS.md`, `figures/`

Reproduce: `python3 scripts/build_items.py && python3 scripts/stats_pws_safebench.py` (recomputes every number from the JSONL). Re-running the arms requires vendor keys and the Asha benchmark key.

Headline (either-judge rule): GPT-5.5 8/60, Claude Sonnet 5.5 7/60, Gemini 3.8 Flash 7/60, Asha 10/60 unsafe; no pairwise difference (Holm p = 1). Pre-registered H1 FAIL, reported as such. See `RESULTS.md`.

## Hard v1.1 replicate run (post hoc, 2026-10-04)

`results_hard_rep/` repeats the Hard v1.1 comparison under identical settings: ChatGPT (`gpt-5.5-2026-04-23`), Gemini 3.8 Flash and Asha production re-queried on 2026-10-04; the Apex-J arm is the incumbent replicate from `apex_pws/results/dev_C0rep*` (relabeled `apexj`). Scored with the same judges and the same CUTOFF adjudication (`HARD_RES_DIR=results_hard_rep python3 scripts/rejudge_cutoff.py`, then `scripts/stats_hard.py --adjudicated`). `replicate_summary.json` holds per-arm run-to-run McNemar tests and pooled Wilcoxon signed-rank comparisons (Holm, six pairs).

Unsafe items, run 1 / run 2 (adjudicated): ChatGPT 26 / 29, Gemini 23 / 24, Asha production 14 / 19, Apex-J 9 / 13 of 96. Pooled over both runs, Apex-J was lower than ChatGPT (Holm p < 0.001) and Gemini (p = 0.015); production was lower than ChatGPT (p = 0.046), not Gemini (p = 0.243).
