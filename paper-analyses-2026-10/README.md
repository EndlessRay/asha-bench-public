# Analyses for the nonmaleficence paper (October 2026)

Scripts and outputs behind the statistics in Singh and Anand, "Nonmaleficence First" (JAMA Network Open submission and its preprint companion). Every number the paper cites from the HealthBench 5,000-item run, the psychosis-bench run and the small-sample tests is in `research/analysis/SUMMARY.md` with its method.

- `_tools/council_analyses.py`: paired score differences (item bootstrap), the harm proxy under three estimators with Holm and Bonferroni adjustment, tails, length tertiles, the equal-length gain, grader agreement, Hard vs non-Hard headroom, and the psychosis-bench scenario-level sign test.
- `_tools/verify_council_analyses.py`: an independent second computation path; writes `research/analysis/verification.csv` and fails on any mismatch.
- `_tools/harm_ci.py`: the original criterion-pooled harm-proxy bootstrap (`research/harm_ci.csv`).

Reproduce from the repository root:

```bash
curl -sSL -o /tmp/hb_hard.jsonl https://openaipublic.blob.core.windows.net/simple-evals/healthbench/hard_2025-05-08-21-00-10.jsonl
ASHA_BENCH="$PWD" HB_HARD=/tmp/hb_hard.jsonl python3 paper-analyses-2026-10/_tools/council_analyses.py
ASHA_BENCH="$PWD" HB_HARD=/tmp/hb_hard.jsonl python3 paper-analyses-2026-10/_tools/verify_council_analyses.py
```

Requires Python 3.10+ with numpy and scipy. Seeds are fixed; reruns are byte-identical.
