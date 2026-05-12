#!/usr/bin/env python3
"""Verify the upstream Au Yeung 2025 Psychosis-bench scenarios SHA-256.

Reproduces the SHA-256 locked in data/DATASET_LOCK.md by fetching the upstream
test_cases.json over HTTPS (no auth) and hashing the bytes.

Exits 0 on match, 1 on mismatch. Prints both expected and observed hashes.
"""
import hashlib
import sys
import urllib.request

EXPECTED = "d9b7820c0bebb6ec845e5825378535e8e35b79b0244a72be64ec5e49d8da439f"
URL = "https://raw.githubusercontent.com/w-is-h/psychosis-bench/main/data/test_cases.json"


def main() -> int:
    print(f"fetching {URL}")
    with urllib.request.urlopen(URL, timeout=30) as resp:
        body = resp.read()
    observed = hashlib.sha256(body).hexdigest()
    print(f"expected SHA-256 (locked in data/DATASET_LOCK.md): {EXPECTED}")
    print(f"observed SHA-256                                 : {observed}")
    print(f"bytes                                             : {len(body):,}")
    if observed == EXPECTED:
        print("\nOK — bit-exact match with the locked dataset.")
        return 0
    print("\nMISMATCH — upstream has moved or the local lock is stale.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
