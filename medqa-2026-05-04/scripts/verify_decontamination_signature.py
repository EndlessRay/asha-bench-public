#!/usr/bin/env python3
"""Verify the L1 decontamination audit signature on the 2026-05-04 MedQA run.

The Citadel benchmark harness `tests/benchmarks/medqa_8arm.py` excludes the
private `medqa_usmle` Qdrant collection from KIL retrieval on every query.
This is threaded through `set_kil_exclude_collections()` into the KIL service,
and the resulting exclude list is echoed back to the caller in each response's
`meta.exclude` field.

This script audits the parent run file (which is NOT redistributed in
bench-public/ because it contains full response text) and verifies that 1273
of 1273 Asha records carry `meta.exclude = ["medqa_usmle"]`. If you have the
parent file, run:

    python3 verify_decontamination_signature.py /path/to/medqa_6arm_20260504_060220.json

Expected output:
    n records:            1273
    with exclude flag:    1273
    distinct values:      {'medqa_usmle'}
    decontamination L1:   VERIFIED

If your file shows a different count, the audit signature does not match the
bench-public bundle and you do not have the same source run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(path_arg: str) -> int:
    p = Path(path_arg)
    if not p.is_file():
        print(f"ERROR: not a file: {p}", file=sys.stderr)
        return 2
    d = json.loads(p.read_text())
    n = 0
    with_excl = 0
    distinct = set()
    for r in d.get("results", []):
        meta = (r.get("asha") or {}).get("meta") or {}
        n += 1
        ex = meta.get("exclude")
        if ex:
            with_excl += 1
            if isinstance(ex, list):
                distinct.update(ex)
            else:
                distinct.add(str(ex))
    print(f"n records:           {n}")
    print(f"with exclude flag:   {with_excl}")
    print(f"distinct values:     {distinct}")
    ok = (n == 1273 and with_excl == 1273 and distinct == {"medqa_usmle"})
    print(f"decontamination L1:  {'VERIFIED' if ok else 'MISMATCH'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
