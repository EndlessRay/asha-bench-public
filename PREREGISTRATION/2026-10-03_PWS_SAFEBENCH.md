# Pre-registration: PWS-SafeBench (v1.0, Hard v1.1, remediation ladder)

Three locks, each committed in the authors' development repository before the first affected model call, and mirrored here with the files unchanged:

| Lock | Development-repo commit | Committed (America/New_York) | Artifact SHA-256 |
|---|---|---|---|
| PWS-SafeBench v1.0 item bank + `PREREGISTRATION.md` + protocol | `39911be9` | 2026-10-03 15:46:36 | `e2312422a41bec58d911ef857d81d6004811628a74a6b52c41b2708d8e2728cf` (`data/pws_safebench_v1.0.json`) |
| PWS-SafeBench Hard v1.1 bank + `PREREGISTRATION_HARD_v1.1.md` | `5ad814cb` | 2026-10-03 17:38:39 | `358011e97b6e9f393b5841dd99716132ed3dc47b042b26f1eabc4abba9aaed19` (`data/pws_safebench_hard_v1.1.json`) |
| Apex-PWS remediation ladder plan, configs, held-out v1.2 bank | `30a018e0` | 2026-10-03 20:41:15 | see `apex_pws/PLAN.md` |

Amendments (each a separate dated file in `pws-safebench-2026-10/`, each made before the first affected response): `PREREGISTRATION_AMENDMENT_1.md` (output-token ceilings, v1.0), `PREREGISTRATION_AMENDMENT_2.md` (repository ignore rule that had excluded the bank files), `PREREGISTRATION_AMENDMENT_3.md` (deprecated `gpt-5.3-chat-latest` alias replaced by `gpt-5.5-2026-04-23`).

Verification: recompute `sha256sum` of the bank files in `pws-safebench-2026-10/data/` and compare with the hashes recorded inside the pre-registration documents. The development repository is private; the push date of this directory to the public repository is a later bound on the lock, and the commit timestamps above are the earlier bound reported by the authors.

Files: `pws-safebench-2026-10/PREREGISTRATION.md`, `pws-safebench-2026-10/PREREGISTRATION_HARD_v1.1.md`, `pws-safebench-2026-10/PROTOCOL.md`.
