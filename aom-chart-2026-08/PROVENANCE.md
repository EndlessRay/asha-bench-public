# Provenance and Audit Trail

Every production change involved in this result, in order, on
`EndlessRay/Citadel` (private; diffs available to the benchmark author on
request):

| Change | Merged | What it did |
|---|---|---|
| #636 | 2026-08-25 | `clinical_guidelines_v4` ingestion pipeline (21,139 PubMed practice-guideline records + 12 physician-verified AAP/AAFP 2013 AOM key-action summaries; issuer + publication-year + PubMed UpdateIn/UpdateOf supersession payloads); lay-glossary fix that had been corrupting "acute" and "apnea" in user-facing text; retrieval channel repoint |
| #637 | 2026-08-25 | PubMed pagination fix (year-sliced fetch) |
| #638 | 2026-08-25 | TIER-1 pediatric AOM protocol block + three general rules: guideline primacy, threshold arithmetic, undocumented-history-is-not-negative-history; blind legacy guideline collections de-wired |
| #639 | 2026-08-25 | Laterality lay terms as grammatical adjectives |
| `f2d4b66a` | 2026-08-25 | Fallback source panel ranked by answer relevance |
| `725d103a` | 2026-08-25 | Streaming source panel gated on answer relevance |
| equity guard | 2026-08-26 | Identity-invariance rule (insurance, caregiver age/occupation, race, names, language never shift the plan or assumed follow-up reliability) + casual-phrasing duration coverage |
| harness | 2026-08-26 | This repo's harness + scorer iterations (all scoring re-derivable from stored raw traces) |

Timeline honesty: the first internal run of the locked protocol
(2026-08-25 morning) FAILED the age cusp and duration and decorated an
irrelevant sleep-apnea citation. The failures above were fixed the same
day at the corpus, prompt, and citation layers; the identity-language
findings were found by our own bias battery overnight and fixed before
any public claim. The before-traces are preserved in
`traces/aom_variants.jsonl` (pre-guard cells) and the original assessment
memo.

Task IDs inside every JSONL row map to the production A2A audit log
(`a2a_tasks` / `a2a_audit_log`) for independent verification.
