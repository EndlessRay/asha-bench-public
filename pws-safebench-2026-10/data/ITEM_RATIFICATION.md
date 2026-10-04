# Item ratification log

Items were drafted by the Lyra and Asha agents from the primary sources listed in `pws_safebench_v1.0.json` and locked at the pre-registration commit so that no model under test was queried before lock. Clinician ratification by the two study physicians happens in the review tool (`Docs/preprint/pws-ai-safety-2026-10/review/`), item by item: approve, or edit with a reason.

Rules:
- An approved item stands as locked.
- An edited item becomes an amendment entry below (date, item id, change, reason). Only that item is re-run for every arm, and the amendment is reported in the results.
- A rejected item is dropped from the primary analysis and listed below; its original responses remain in the public JSONL.

| Date | Item | Action | Change | Reason |
|---|---|---|---|---|
| (pending) | | | | |
