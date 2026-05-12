# Figures for the DNAi public benchmark bundle

Self-contained matplotlib renderer for the six figures that accompany the
Substack post, the LinkedIn / X social drops, and the manuscript at
`Docs/research/hallucination-paper/DRAFT_v1.md`. Every figure regenerates
deterministically from the published bench artifacts in this repo plus a small
inline roster of court filings (verified against `DRAFT_v1.md` Appendix B).

## Reproduce

```bash
cd bench-public/figures
python3 generate_figures.py
```

Outputs land in `figures/output/` as 200-DPI PNGs at the dimensions below.

## Figures

| # | File | Use | Source data |
|---|------|-----|-------------|
| 1 | `01_deaths_timeline.png` | The "why this matters" anchor. Vertical roster of named chatbot-attributed deaths and civil filings, March 2023 to May 2026. Gold stars mark court milestones (Sewell Setzer settlement Jan 2026, Lyons MTD denied Apr 2026). | Inline roster in `generate_figures.py`, verified against `DRAFT_v1.md` Section 1 and Appendix B plus 2026-05-12 web verification pass. |
| 2 | `02_architecture_stack.png` | Explains "what is Asha." Block diagram of the four symbolic components around the LLM. | `../README.md` architecture section (Qdrant 759 collections / 125.44M vectors, CIU counts, patent numbers). |
| 3 | `03_medqa_accuracy.png` | MedQA headline. Five-arm accuracy with Wilson 95% CI and parse-failure annotations. | `../medqa-2026-05-04/results/*.jsonl` (computed values match `../medqa-2026-05-04/reports/01_accuracy_table.md`). |
| 4 | `04_medqa_mechanism.png` | Two-panel: paired McNemar contingency + META_CORRECT rescue waterfall. Connects the +3.22 pp lift to the patented primitive. | `../medqa-2026-05-04/reports/02_paired_asha_vs_gemini.md`. |
| 5 | `05_psychosis_metrics.png` | Psychosis-bench headline, Judge A only. Three panels: DCS, HES, SIS. Asha vs bare Gemini 2.5 Flash. | `../psychosis-bench-2026-05-11/results/aggregate_two_judges.json` (read at runtime). |
| 6 | `06_prereg_scoreboard.png` | The κ-failure-as-a-feature visual. Three pre-registered hypotheses, two PASS, one FAIL, formal verdict INCONCLUSIVE. | `../PREREGISTRATION/2026-05-11_PSYCHOSIS_BENCH.md` and `../psychosis-bench-2026-05-11/reports/02_dual_judge_kappa.md`. |
| 7 | `07_implicit_explicit.png` | Psychosis-bench stratified by scenario condition. Three panels: DCS / HES / SIS by Implicit vs Explicit. Shows whether Asha's lift holds on the harder half (it does on SIS; magnitude shrinks on DCS/HES). | Computed by `analyze_implicit_explicit.py` from `../psychosis-bench-2026-05-11/results/per_turn_judge_a.jsonl`. |
| 8 | `08_medqa_headline.png` | Social-shareable MedQA headline. Five-arm horizontal bar chart with large fonts, Asha bar visually emphasized, prominent parse-failure column, bottom callout with statistical-parity-with-Opus framing and META\_CORRECT attribution. | `../medqa-2026-05-04/results/*.jsonl` and `../medqa-2026-05-04/reports/`. |
| 10 | `10_psychosis_headline.png` | Social-shareable Psychosis-bench headline. Three-panel layout (DCS / HES / SIS) with Judge-A magnitudes large and Asha-versus-Gemini bars stark. Bottom callout strip discloses the κ failure and the Judge-B robustness numbers so the image stays honest when it travels alone. | `../psychosis-bench-2026-05-11/results/aggregate_two_judges.json` (read at runtime). |

## Supporting analysis scripts

These two scripts produce the per-stratum and per-question tables that
appear in the Substack post and the manuscript. Both read directly from the
public per-turn / per-question JSONLs and emit markdown to stdout.

- `analyze_implicit_explicit.py` — Stratifies Psychosis-bench by scenario
  condition (Implicit vs Explicit). Surfaces the implicit/explicit DCS, HES,
  and SIS breakdown and the location of all Asha SIS misses.
- `analyze_medqa_losses.py` — Decomposes the 25 paired losses where Asha
  was wrong and bare Gemini was right on MedQA. Reports the McNemar 2×2
  with parseability conditioning. Surfaces the parseable-only subset finding
  (Asha −0.83 pp on the fair-fight subset; the entire +3.22 pp paired lift
  is attributable to META_CORRECT envelope rescue on bare Gemini's parse
  failures).

## Alt-text (for Substack, LinkedIn, X, accessibility)

**Figure 1.** *Vertical timeline of eleven named individuals and one secondary
victim whose deaths have been linked by court filing or major-outlet reporting
to AI chatbot use, March 2023 through May 2026. For each person, a circle marks
the date of death and a square marks the date the civil complaint was filed,
connected by a bar. Color encodes the AI vendor: Chai, Character.AI, OpenAI,
or Google. Ages range from thirteen to eighty-three. Eight cases are active in
court as of May 12, 2026; two have settled.*

**Figure 2.** *Block diagram of Asha's neurosymbolic architecture. An LLM
verbalization layer sits at the center (Gemini family in production, Anthropic
in research swap-tests). Four symbolic components surround it: Memory (Qdrant,
759 collections, 125.44 million vectors), Knowledge Integration Layer (symbolic
retrieval before every LLM call), Epistemic Arena (31,616 active Competitive
Informational Units), and META_CORRECT (deterministic post-emission corrector,
US Provisional 397222-7002P1). Arrows show the four-stage data flow: retrieve,
synthesize, compete, correct. Parent application US 19/290,471 (allowed).*

**Figure 3.** *Horizontal bar chart of MedQA accuracy across five arms, n equals
1,273. Asha leads at 95.52 percent (Wilson 95% CI 94.24 to 96.53). Claude Opus
4.5 at 94.66 percent, OpenAI o4-mini-high at 93.79 percent, Gemini 3.1 Pro
Preview at 92.30 percent, GPT-4o at 91.59 percent. Parse-failure counts on the
right: Asha zero, Opus one, o4-mini-high thirty-one, Gemini seventy-one,
GPT-4o zero. Asha bar in teal, all others in gray.*

**Figure 4.** *Two-panel figure. Left panel: paired McNemar 2-by-2 contingency
table for Asha versus bare Gemini 3.1 Pro Preview. Cells contain 1,150 both
right, 66 Asha right and Gemini wrong, 25 Asha wrong and Gemini right, 32 both
wrong. Lift +3.22 percentage points, odds ratio 2.64 with 95% confidence
interval 1.67 to 4.18, McNemar exact p equals 2.0 times 10 to the minus 5.
Right panel: three-stage waterfall showing 71 Gemini parse failures rescued by
META_CORRECT into 51 correct answer letters, accounting for 51 of the 66
paired McNemar wins. The remaining 15 paired wins come from KIL evidence
substitution on parseable-but-incorrect Gemini answers.*

**Figure 5.** *Three-panel chart for the Au Yeung 2025 Psychosis-bench, judge
gpt-4o-mini. DCS panel: Asha 0.354, Gemini Flash 1.215, 3.43 times lower for
Asha with bootstrap 95% CI 2.15 to 6.13. HES panel: Asha 0.104, Gemini Flash
0.823, 7.9 times lower with bootstrap 95% CI 4.4 to 22.7. SIS panel: Asha 92
of 96 (95.8 percent, Wilson 95% CI 89.8 to 98.4), Gemini Flash 29 of 96 (30.2
percent, Wilson 95% CI 21.9 to 40.0), absolute gap 65.6 percentage points,
Fisher's exact p approximately 5.7 times 10 to the minus 16.*

**Figure 6.** *Scoreboard of three pre-registered hypotheses for the
Psychosis-bench. H_DCS PASS (3.43 times, bootstrap lower bound 2.15, threshold
was 2.0). H_SIS PASS (Asha Wilson lower bound 0.898 and Gemini Flash Wilson
upper bound 0.400, non-overlapping). H_JUDGE_RELIABILITY FAIL (average kappa
0.249 across two LLM judges, threshold was 0.60). Bottom band: formal verdict
per literal rule is INCONCLUSIVE. Both judges agree on the direction of every
metric. Selective refusal ruled out by parse-failure profile.*

**Figure 7.** *Three-panel stratification of Psychosis-bench by scenario
condition under Judge A (gpt-4o-mini). Implicit panel: DCS Asha 0.569 vs
Gemini Flash 1.028 (1.80 times lower), HES Asha 0.146 vs 0.625 (4.29 times
lower), SIS Asha 44 of 48 = 91.7 percent (Wilson 80.4 to 96.7) vs Gemini
Flash 11 of 48 = 22.9 percent (Wilson 13.3 to 36.5), gap +68.8 percentage
points. Explicit panel: DCS Asha 0.139 vs Gemini Flash 1.403 (10.10 times
lower), HES Asha 0.062 vs 1.021 (16.33 times lower), SIS Asha 48 of 48 =
100.0 percent vs Gemini Flash 18 of 48 = 37.5 percent (Wilson 25.2 to 51.6),
gap +62.5 percentage points. All four of Asha's SIS misses across the full
bench live in implicit scenarios.*

**Figure 8.** *Social-shareable horizontal bar chart of MedQA accuracy across
five arms, n equals 1,273. Asha bar (teal, thicker border) at the top at 95.52
percent. Claude Opus 4.5 at 94.66 percent, OpenAI o4-mini-high at 93.79 percent,
Gemini 3.1 Pro Preview at 92.30 percent, GPT-4o at 91.59 percent. Parse-failure
column to the right: Asha zero, Opus one, o4-mini-high thirty-one, Gemini
seventy-one, GPT-4o zero. Bottom callout: Asha matches Claude Opus 4.5 to
statistical parity (paired McNemar exact p equals 0.228) at roughly one-quarter
the marginal per-query cost; zero parse failures across 1,273 questions; bare
Gemini 3.1 Pro Preview seventy-one parse failures (5.58 percent); META_CORRECT
envelope rescue accounts for the entire 3.22 percentage-point paired McNemar
advantage.*

**Figure 10.** *Social-shareable three-panel chart of the Psychosis-bench
headline numbers under Judge A (gpt-4o-mini, temperature zero,
protocol-specified). Delusion Confirmation panel: Asha 0.354 versus Gemini 2.5
Flash 1.215, 3.43 times lower with scenario-paired bootstrap 95 percent
confidence interval 2.15 to 6.13. Harm Enablement panel: Asha 0.104 versus
Gemini 2.5 Flash 0.823, 7.9 times lower with bootstrap 95 percent confidence
interval 4.4 to 22.7. Safety Intervention rate panel: Asha 92 of 96 equals
95.8 percent (Wilson 89.8 to 98.4) versus Gemini 2.5 Flash 29 of 96 equals 30.2
percent (Wilson 21.9 to 40.0), absolute gap 65.6 percentage points, Fisher's
exact p approximately 5.7 times 10 to the minus 16. Bottom callout strip
discloses the pre-registered judge-reliability gate failure (average kappa
equals 0.249), the Judge B (claude-haiku-4-5) magnitudes (1.72 times DCS, 1.76
times HES, plus 22.9 percentage points SIS) under which direction holds and
magnitude shrinks, and the formal verdict per literal pre-registration rule of
INCONCLUSIVE.*

## Design system

- Palette is consistent across all six figures. Asha teal `#1F6F52`, neutral
  gray `#9CA3AF` for baselines, muted red `#B8423A` for failures, gold
  `#C8975B` for the patented primitive callout.
- Fonts default to DejaVu Sans (matplotlib default; renders cleanly across
  Linux, macOS, and Windows without external font files).
- All figures render at 200 DPI as PNG, sized for both Substack inline and
  Twitter/LinkedIn cards.
- No emojis, no slogans, no em-dashes in figure prose.

## Prose discipline note

Caption text on every figure follows the same prose rules as the Substack and
the manuscript: no em-dashes, no "X, not Y" constructions, no fragment
sentences, no slogans. If a future contributor adds a figure that violates
these rules, the Substack will not pass the prose audit and the bench bundle
will not be internally consistent.
