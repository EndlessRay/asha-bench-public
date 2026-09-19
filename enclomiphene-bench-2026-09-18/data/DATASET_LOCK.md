# Dataset lock

SHA-256 of the two question files as run on 2026-09-18 (identical to `scripts/audits/enclomiphene_bench/data/` at commit b3c64c6a, merged in PR #977).

```
0d685bcf733e8eeabef277bc363d55c7a63785916cd4904a2eb9ca0e769aad44  enclomiphene_psychosis_cases.json
5bdd161987b7d732db1715492e2d1f0149eeedc33f40685ee0e2953bc44a7246  enclomiphene_healthbench_redteam.jsonl
```

Verify: `cd data && shasum -a 256 -c <<< "$(sed -n 6,7p DATASET_LOCK.md)"`
