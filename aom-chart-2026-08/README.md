# Asha on the aom-chart Locked Pediatric AOM Protocol

Verbatim traces of [Asha](https://askasha.org), DNAi Systems' fiduciary
medical agent, on the locked 24-month acute otitis media chart published by
Dr. Michael Hobbs in [dochobbs/aom-chart](https://github.com/dochobbs/aom-chart)
(packet v5). The run covers his CDS stem, his identity-variant bias arm, his
18-month counter-stem, and his sealed turn-2 question.

These are self-run receipts. The authoritative scoreboard belongs to the
benchmark author, and nothing here assigns Asha a row on it.

## Results

All traces below come from one production build, run 2026-08-26, serially,
through the same pipeline that serves live traffic.

| Suite | N | Result |
|---|---|---|
| Locked 24-month stem | 14 | 14/14 correct: shared decision with safety-net mechanics, 7-day course, stated boundary arithmetic ("24 months equals 2.0 years, the 2-years-and-older stratum"), 80-90 mg/kg/day with weight math |
| Identity variants, all 14 published cells | 36 | Plan eligibility, duration, stratum, and dose invariant across insurance, race, names, caregiver age, occupation, and interpreter cells; zero adverse reliability inferences |
| 18-month counter-stem | 5 | 5/5 kept the 10-day course and the 6-to-23-month stratum, so the 24-month boundary rule generalizes rather than memorizes |
| Casual phrasing probe | 4 | 4/4 presented the severity-stratified durations and placed a 2-year-old in the 2-through-5-year band |
| Sealed turn 2 (askasha.org UI) | 1 session | Asked for prior-30-day antibiotics, prior AOM history, and follow-up reliability; invented nothing; stated unprompted that race and insurance do not enter the clinical decision |

Known imperfection, quantified: in roughly 1 to 2 of every 10 runs the
amoxicillin-clavulanate trigger check is phrased as an assertion followed by
a confirm-with-the-caregiver directive, rather than the stricter declared
form ("I am assuming..."). The affected rows are flagged in the traces.

## Scoring

Each JSONL row carries the full response, its production task id, latency,
and an automated codebook screen (plan, snap, duration, stratum, dose,
fabrication, reliability and identity language) implemented in
`harness/aom_chart_harness.py`. The automated screen under-extracts some
duration phrasings, so every flagged row was hand-reviewed against
`docs/codebook_v2.md`; the hand-verified tables in `traces/SUMMARY.md` are
authoritative, and `--rescore` re-derives the automated layer from the
stored traces.

## Method

- One A2A API call per replicate against production, stateless, no system
  prompt injected, matching the CDS-arm methodology of the source repo. The
  UI sessions used a fresh anonymous browser session per conversation.
- There is no benchmark-specific routing or detection in the product. There
  is benchmark-motivated hardening, described plainly: after the author's
  post surfaced real defects, we ingested a 22,846-document clinical
  practice guideline corpus (all issuers, with publication-year anchoring
  and supersession links), added three general reasoning rules (age and
  threshold boundary arithmetic, declared assumptions for undocumented
  history, identity invariance), and added pediatric AOM to the same
  standard-of-care protocol set that already covered pediatric diarrhea,
  adrenal crisis, pheochromocytoma, and elder mistreatment. The 18-month
  counter-stem exists in this dataset to test that distinction.
- Replication guidance for conversational tools, ours included: run each
  replicate in a fresh session. Memory features can carry context between
  same-session runs; `PROVENANCE.md` documents the one instance our own
  battery caught during development.

## License

Traces and harness: MIT. The stem, variants, and codebook belong to
[dochobbs/aom-chart](https://github.com/dochobbs/aom-chart) and are
reproduced only as needed for reproducibility.
