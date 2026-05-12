#!/usr/bin/env python3
"""Verify the input MedQA dataset SHA-256 against the locked value.

Usage:
    python3 verify_dataset_sha.py /path/to/medqa_usmle_4opt_test.jsonl
"""
import hashlib
import sys
from pathlib import Path

EXPECTED_SHA = "c3b905ccfa66152dc25afbcb2c10e86c0bdb208824f0658fcdb2c040f60a2beb"
EXPECTED_N = 1273


def main(path_arg: str) -> int:
    p = Path(path_arg)
    if not p.is_file():
        print(f"ERROR: not a file: {p}", file=sys.stderr)
        return 2
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    n = sum(1 for _ in p.open())
    ok_sha = sha == EXPECTED_SHA
    ok_n = n == EXPECTED_N
    print(f"file:       {p}")
    print(f"SHA-256:    {sha}")
    print(f"expected:   {EXPECTED_SHA}")
    print(f"match:      {'YES' if ok_sha else 'NO'}")
    print(f"line count: {n} (expected {EXPECTED_N}): {'YES' if ok_n else 'NO'}")
    return 0 if (ok_sha and ok_n) else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
