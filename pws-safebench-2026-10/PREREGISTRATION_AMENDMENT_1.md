# Pre-registration amendment 1 (2026-10-03, before first query)

**Timing.** Lock commit `39911be9` at 15:46:36 EDT. This amendment was applied at approximately 15:48 EDT, before the first model query (the one-item smoke test that preceded the full run). No response from any arm existed when it was made.

**Change.** Output-token ceilings for the consumer arms were raised to avoid the truncation failure documented in the 2026-05-12 psychosis-attribution bench (thinking models spend their output budget on reasoning tokens and return empty text):

| Arm | Locked value | Amended value |
|---|---|---|
| `gpt` (gpt-5.5-2026-04-23) | `max_completion_tokens=2048` | `max_completion_tokens=8192` (reasoning tokens count against this budget) |
| `claude` (claude-sonnet-5-5) | `max_tokens=2048` | `max_tokens=4096` |
| `gemini` (gemini-3.8-flash) | vendor default | unchanged |
| `asha` | n/a | unchanged |

**Nothing else changed.** Items, arms, judges, endpoints, rules and statistics are as locked. The harness (`scripts/run_pws_safebench.py`) carries the amended values; the locked file is left byte-identical to the commit.
