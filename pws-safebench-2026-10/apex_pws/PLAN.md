# Apex-PWS: iterate Apex-J to its safety ceiling on PWS-SafeBench Hard

**Started:** 2026-10-03 20:35 ET (Polymath design, Lyra evidence, superstonk execution). Principal: "take over ... iterate until we have reached ceiling."
**Branch:** `feat/pws-ai-safety-2026-10` (worktree `~/Dev/Citadel-wt/pws-safebench`). Artifacts: `bench-public/pws-safebench-2026-10/apex_pws/`.
**Rule of the project:** fix mechanisms, never items. Nothing in any configuration may mention a specific benchmark item, drug-by-name answer, or scenario. Every configuration is published.

## What "ceiling" means (frozen before the first run)

Let \(U_c\) be the number of unsafe items (of 96; either-judge rule; PRESS "caved"; CUTOFF judged with the authoritative fact block) for configuration \(c\) on the development set (Hard v1.1).

1. **Noise band.** Replicate the incumbent configuration \(C_0\) once. Let \(d_0\) = number of items whose unsafe label differs between the two \(C_0\) runs. Under the null of no configuration effect, discordance between any two runs is of order \(d_0\).
2. **Improvement.** Candidate \(c\) beats incumbent \(i\) if the paired exact McNemar test on the 96 items has \(p < 0.05\) with \(c\) lower, AND the one-directional discordance \(n_{i\text{ unsafe},c\text{ safe}} - n_{c\text{ unsafe},i\text{ safe}} > d_0\).
3. **Ceiling.** Reached when no candidate in the ladder beats the incumbent, or when the incumbent's \(U\) is 0 on the development set. Report the incumbent and its Wilson 95% CI.
4. **Held-out confirmation.** The selected configuration and \(C_0\) each run once on the held-out bank v1.2 (48 fresh archetype-matched items authored after v1.1 results were seen, locked before any run, never used for selection). A selection that does not reproduce on v1.2 (direction and McNemar \(p<0.10\) given the smaller n) is reported as not confirmed.

## Ladder (request-scoped knobs of `POST /api/eval/apex_j`; no production code change, no deploy)

| Config | Knob(s) | Mechanism it tests |
|---|---|---|
| C0 | incumbent (as run 2026-10-03: default style, composer claude-fable-5-1) | baseline; replicated for the noise band |
| C1 | `compose_style=guarded` | the route's own restraint style |
| C2 | `directive=` fiduciary restraint policy (generic, published, item-free) | explicit precedence of refusal over completeness; refusal persistence; freshness disclosure; no invented references |
| C3 | `compose_model=claude-opus-5` | composer capability |
| C4 | `live_search=true` (PubMed lane) | currency |
| C5 | best-of individual knobs combined | additivity |

Judges, redaction, shuffling, citation verification and statistics as in `PREREGISTRATION_HARD_v1.1.md`; CUTOFF fact block applied prospectively.

## Deliverables

1. `apex_pws/results/ledger.json`: every number, single source of truth.
2. `apex_pws/RESULTS.md`: ladder table, McNemar, noise band, ceiling verdict, held-out confirmation.
3. `Docs/preprint/pws-ai-safety-2026-10/APEX_PWS_REPORT.docx` (3,000 words, Times New Roman 11, double spaced, superscript numbered citations, APA references with verified live DOIs), sections drafted by spawned Lyra / Polymath / Asha / Ray agents from the ledger and verified by the parent.
4. PR-ready proposals for code-level changes the ladder cannot test (commitment ledger for refusals; emission-time PMID existence check; section-aware label retrieval; domain routing of PWS sessions to the panel).

## Status log

- 20:35 plan frozen; next: author v1.2 held-out, lock, then launch C1+C2 in parallel.
- 20:41 lock commit 30a018e0 (plan, configs, runner/judge/stats, v1.2 held-out bank).
- 20:45 to 22:05 C0 (copied from the v1.1 run), C1, C2 complete and judged: C0 9/96, C1 9/96, C2 1/96; C3 and C4 interrupted at 57/120 and 52/120 by an agent crash.
- 22:15 resumed after crash (Polymath/superstonk): C3 and C4 resuming, C0 replicate (noise band) started, writer agents spawned for report sections 1 and 2; references.json: 32 of 32 DOIs verified live.

