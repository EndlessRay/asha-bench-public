# DATASET_LOCK — Au Yeung 2025 Psychosis-bench scenarios

Upstream URL (canonical, **preprint repo**):
```
https://raw.githubusercontent.com/w-is-h/psychosis-bench/main/data/test_cases.json
```

Verified locally on 2026-05-12:

```
SHA-256 d9b7820c0bebb6ec845e5825378535e8e35b79b0244a72be64ec5e49d8da439f
bytes   30,544
cases   16  (8 archetypes × 2 phrasings: explicit / implicit)
turns   12  per case (Phases 1-4 escalation)
```

Cite as: Au Yeung, J., Dalmasso, J., Foschini, L., Dobson, R. J. B., & Kraljevic, Z. (2025), *The Psychogenic Machine: Simulating AI Psychosis, Delusion Reinforcement and Harm Enablement in Large Language Models*, [arXiv:2509.10970v2](https://arxiv.org/abs/2509.10970) — **preprint, not peer-reviewed**.

## Verify

```
python3 scripts/verify_scenarios_sha.py
```
