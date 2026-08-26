# Provenance

The production changes behind this result, in order, on `EndlessRay/Citadel`
(private; diffs available to the benchmark author on request):

| Change | Merged | What it did |
|---|---|---|
| #636 | 2026-08-25 | `clinical_guidelines_v4` corpus: 21,139 PubMed practice-guideline records plus 12 physician-verified AAP/AAFP 2013 AOM key-action summaries, with issuer, publication-year, and supersession payloads; lay-glossary repair; retrieval channel repoint |
| #637 | 2026-08-25 | PubMed pagination fix for the ingestion pipeline |
| #638 | 2026-08-25 | Pediatric AOM standard-of-care protocol block; general rules for guideline primacy, threshold arithmetic, and undocumented history; blind legacy guideline collections de-wired |
| #639 | 2026-08-25 | Laterality lay terms as grammatical adjectives |
| `f2d4b66a`, `725d103a` | 2026-08-25 | Source panels gated on answer relevance |
| `672e977e` | 2026-08-25 | Identity-invariance rule and casual-phrasing duration coverage |

Context, stated once: the author's LinkedIn post prompted us to run his
protocol internally on 2026-08-25, and that first run surfaced real defects
(age-cusp misapplication, a broken guidelines retrieval channel, corrupted
lay terminology, irrelevant citations). The changes above fixed them at the
corpus, prompt, and citation layers the same day. During development we also
ran the identity-variant arm, found identity-conditioned follow-up
assumptions in a minority of runs, and shipped the identity-invariance rule
before publishing anything. Development-phase traces predating the final
build are retained internally and available to the benchmark author on
request; the published dataset is the final build only.

Every JSONL row's task id maps to the production A2A audit log for
independent verification.
