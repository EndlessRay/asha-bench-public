# Pre-registration amendment 2 (2026-10-03, repository hygiene, no content change)

The repository's root `.gitignore` excludes `Data/`, which on a case-insensitive filesystem also matched this bundle's `data/` directory. As a result the lock commit `39911be9` recorded the item bank's SHA-256 in `PREREGISTRATION.md` but did not carry the bank file itself (nor `ITEM_RATIFICATION.md`). This amendment force-adds:

- `data/pws_safebench_v1.0.json`, SHA-256 `e2312422a41bec58d911ef857d81d6004811628a74a6b52c41b2708d8e2728cf`, byte-identical to the value recorded at `39911be9` (verify: `git show 39911be9:bench-public/pws-safebench-2026-10/PREREGISTRATION.md | grep e2312422`), and
- `data/pws_safebench_hard_v1.1.json`, SHA-256 `358011e97b6e9f393b5841dd99716132ed3dc47b042b26f1eabc4abba9aaed19`, recorded in `PREREGISTRATION_HARD_v1.1.md` in the same commit as this file, before any v1.1 query.

The hash recorded at lock is the binding element; the file is now published so anyone can check it.
