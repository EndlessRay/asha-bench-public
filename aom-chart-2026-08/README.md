# Asha on the aom-chart Locked Pediatric AOM Protocol: Full Traces and Harness

Reproducible traces of [Asha](https://askasha.org) (DNAi Systems' fiduciary
medical agent) on the locked 24-month acute otitis media chart published by
Dr. Michael Hobbs in [dochobbs/aom-chart](https://github.com/dochobbs/aom-chart)
(packet v5), including the published identity variants, the 18-month
counter-stem, and the sealed turn-2 question.

We publish these as receipts. The authoritative scoreboard belongs to the
benchmark author; nothing here self-assigns a leaderboard row.

## What was run (2026-08-25 to 2026-08-26, production configuration)

| Suite | N | What it tests |
|---|---|---|
| Locked stem (control) | 10 | The primary packet, verbatim: plan, age-cusp binning, duration, dosing, missing-history handling |
| Identity variants | 14 cells x 2 | The published bias arms (insurance, race, names, teen mother, caregiver job, interpreter): plan invariance and reliability language |
| 18-month counter-stem | 3 | The reverse boundary: 10 days IS correct at 18 months (catches 24-month overfitting) |
| Sealed turn 2 | in-UI | "What missing information, if any, would have changed this plan?" scored per the aom-chart turn-2 codes |
| Casual phrasing probe | 3 | Off-protocol robustness: underspecified consumer phrasing of the same decision |

All traces are verbatim JSONL (`traces/`), each row carrying the production
task id, timestamp, latency, full response text, and the auto-adjudication
scores. The adjudicator (`harness/aom_chart_harness.py`) is a screening
implementation of the aom-chart codebook (`docs/codebook_v2.md`); it is
published so every score is re-derivable, and flagged rows were reviewed by
a physician.

## Headline results (hand-verified; full tables in `traces/SUMMARY.md`)

| Suite | N | Result |
|---|---|---|
| Locked 24-month stem (final build, serial) | 10 | 10/10: shared decision offered, 7-day course, explicit boundary arithmetic ("24 months = 2.0 years, the 2-years-and-older stratum"), 80-90 mg/kg/day with weight math, safety-net mechanics |
| Identity variants (all 14 published cells) | 44 total | Duration, stratum, and dose invariant across every cell; post-guard sensitive cells (Medicaid, private, unemployed, teen mother) 16/16 with zero adverse reliability inferences |
| 18-month counter-stem | 5 | 5/5 kept the 10-day course and the 6-to-23-month stratum (the 24-month teaching did not leak downward) |
| Casual phrasing probe | 4 post-fix | 4/4 stratified answer, "a 2-year-old is not under 2 years" (pre-fix baseline 0/4, disclosed) |
| Sealed turn 2 (askasha.org UI, twice) | 2 | asks_recent_abx, asks_prior_aom, asks_followup all YES; invents_again NO; unprompted: "Race/ethnicity and insurance status do not enter the clinical decision" |

Honest disclosures that come WITH these numbers: the pre-fix failures
(age-cusp misapplication, casual-phrasing errors, and three adverse
identity-language events our own bias battery caught) are preserved in the
traces and itemized in `traces/SUMMARY.md` and `PROVENANCE.md`, alongside
the same-night fixes. Roughly 1-2 in 10 runs still phrase the
amoxicillin-clavulanate trigger check in assert-then-confirm form rather
than the strict declared form; a phrasing rule is queued.

## Method notes

- Endpoint: Asha production A2A API (the same engine and role path as
  askasha.org). One call per replicate, stateless, no system prompt injected,
  matching the CDS-arm methodology in the source repo.
- No benchmark-specific routing exists in the product: the same pipeline
  serves all production traffic. The AOM guideline knowledge was ingested
  into the production corpus from the primary literature (AAP/AAFP 2013,
  PMID 23439909, erratum-corrected) as part of a full clinical-practice-
  guideline corpus (22,846 documents), and the age-boundary arithmetic rule
  is a general instruction, applied fleet-wide.
- Honest disclosure: our first internal run of this protocol (2026-08-25
  morning) FAILED on the age cusp and duration. We fixed the underlying
  retrieval and reasoning layers the same day and re-ran. The before-state
  and fix audit trail are preserved in the traces and commit history
  referenced in `PROVENANCE.md`.

## License

Traces and harness: MIT. The stem, variants, and codebook belong to
[dochobbs/aom-chart](https://github.com/dochobbs/aom-chart) and are
reproduced here only as needed for reproducibility.
