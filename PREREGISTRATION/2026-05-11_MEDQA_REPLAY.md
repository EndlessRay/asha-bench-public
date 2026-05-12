# Pre-registration — MedQA 2026-05-04 forensic replay

**Pre-registered**: 2026-05-11
**Author**: DNAi Polymath audit team
**Run audited**: MedQA 2026-05-04 single-shot 5-arm benchmark

## Context

On 2026-05-04 DNAi ran a 5-arm MedQA single-shot benchmark and reported preliminary results, including a public claim that Asha (single-shot deployed configuration, internally labeled "Asha-Plain" to distinguish from the experimental "Asha-Medprompt" k=5 ensemble that we did NOT report as the headline) achieved 95.52% on n=1,273 with a +3.22 pp paired McNemar lift over bare Gemini 3.1 Pro Preview. The original write-up also asserted that Asha's errors were "statistically independent of Gemini's parametric priors" based on a 11/32 = 34.4% same-letter rate on the both-wrong subset.

This pre-registration commits — before the retest is run — the hypotheses, methodology, and acceptance criteria for an independent forensic replay using the saved raw response files.

## Hypotheses (committed before retest)

| ID | Hypothesis | Pre-reg expectation |
|----|-----------|---------------------|
| H1 | Per-arm accuracy reproduces bit-exact from the saved per-question responses with the documented Lyra-lenient parser. | PASS if all 5 arms reproduce ±0 questions. |
| H2 | The +3.22 pp paired McNemar lift of Asha vs bare Gemini reproduces with the same (a, b, c, d) cells. | PASS if (a, b, c, d) = (1150, 66, 25, 32). |
| H3 | The "errors are independent" claim (11/32 = 34.4% same-letter, H0=1/3, p≈1.0) is robust to parser conditioning. | If, after excluding cells where one arm is unparseable (cannot share a letter), the same-letter rate stays near 1/3 and p stays > 0.10, PASS. Otherwise, the original claim is OVERTURNED and must be retracted. |
| H4 | Asha vs Claude Opus 4.5 paired McNemar test: at α=0.05 the lift is statistically significant. | Pre-reg expectation: FAIL — based on a back-of-the-envelope calculation we did not expect a 0.86 pp lift on n=1273 to clear α=0.05. We commit to publishing whatever the test shows. |

## Acceptance criteria

1. Every reported number must be reproducible by running `bench-public/medqa-2026-05-04/scripts/*.py` against the per-question records in `bench-public/medqa-2026-05-04/results/`.
2. The Lyra-style lenient parser used for primary analysis must be the same uniform parser across all arms (no per-arm parser tuning).
3. Any hypothesis that comes out OVERTURNED triggers a retraction in our public-facing materials (YC submission, press, marketing site) within 24 hours of the retest result.
4. Original artifacts (raw response text per arm) remain immutable in the source results directory; the public bundle stores only the parser-output records (qid, gold, predicted, parsed, correct, metadata) — sufficient for bit-exact statistical replay but not redistributing MedQA question text.

## Method

- **Parser**: Lyra-style lenient regex tolerant of `Answer: X`, `\boxed{X}`, `**Answer: X**`, `option X`, `final answer X`, etc. Same parser used uniformly across all arms.
- **Paired test**: McNemar exact two-sided binomial on the (b, c) discordant cells. Wilson 95% CIs reported for proportions.
- **Wrong-letter test**: Restrict to the subset where BOTH arms produced a parseable wrong letter. Two-sided exact binomial test against H0 = 1/3.
- **No multiple-comparison correction needed** for the headline (Asha vs Gemini) test, which is the single pre-registered primary comparison. The pairwise matrix in `reports/02_pairwise_matrix.csv` is exploratory and unadjusted; we will not draw α=0.05 conclusions from it without Benjamini-Hochberg correction.

## Disclosure rules

If H3 is overturned, the original 2026-05-04 wording is retracted publicly with the corrected number. If H4 fails (Asha ≈ Opus on accuracy), we reframe the YC/marketing claim from "Asha beats Opus" to "Asha matches Opus on accuracy at a fraction of the cost" — which is the honest Pareto framing.
