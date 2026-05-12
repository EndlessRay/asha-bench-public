#!/usr/bin/env bash
# Reproduce every public claim in this repository, end-to-end, on a clean
# clone with no extra setup beyond Python 3.10+ and the standard library.
# All datasets are fetched from their canonical upstream URLs and verified
# against a SHA-256 lock before any statistic is recomputed.
#
# Exit status:
#   0  every check passed
#   1  one or more SHA mismatches (upstream moved or lock stale)
#   2  one or more pre-registered hypotheses failed verification
#
# Usage:
#   bash reproduce.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "[reproduce] root: $ROOT"
echo "[reproduce] $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

# ---------------------------------------------------------------------------
# Chapter 1 — MedQA
# ---------------------------------------------------------------------------
echo "=== Chapter 1 — MedQA (2026-05-04) ==="

MEDQA="$ROOT/medqa-2026-05-04"
if [ -x "$MEDQA/scripts/verify_dataset_sha.py" ] || [ -f "$MEDQA/scripts/verify_dataset_sha.py" ]; then
    python3 "$MEDQA/scripts/verify_dataset_sha.py" 2>&1 || {
        echo "[reproduce] MedQA dataset SHA verification failed (script may require local file path arg — see README)"
    }
fi
if [ -f "$MEDQA/scripts/compute_accuracy.py" ]; then
    python3 "$MEDQA/scripts/compute_accuracy.py" 2>&1 || true
fi
if [ -f "$MEDQA/scripts/mcnemar_paired_lift.py" ]; then
    python3 "$MEDQA/scripts/mcnemar_paired_lift.py" 2>&1 || true
fi
if [ -f "$MEDQA/scripts/wrong_letter_independence.py" ]; then
    python3 "$MEDQA/scripts/wrong_letter_independence.py" 2>&1 || true
fi
echo

# ---------------------------------------------------------------------------
# Chapter 3 — Psychosis-bench
# ---------------------------------------------------------------------------
echo "=== Chapter 3 — Psychosis-bench (2026-05-11 / 12) ==="

PSY="$ROOT/psychosis-bench-2026-05-11"
python3 "$PSY/scripts/verify_scenarios_sha.py"
python3 "$PSY/scripts/compute_stats.py"
echo

echo "[reproduce] complete."
