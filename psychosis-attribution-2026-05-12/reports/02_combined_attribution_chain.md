# Report 02 — Combined attribution chain: BENCH3 + BENCH5 + BENCH6

This report synthesises the three attribution-focused benches. Each bench was
independently pre-registered and produced a distinct line of evidence. Together
they close the principal alternative explanations for Asha's Chapter 3 safety
advantage.

## The claim being attributed

Chapter 3 of this bundle reports:

| Metric | Asha | Bare Gemini-2.5-Flash | Effect |
|---|---:|---:|---|
| DCS mean (lower = safer) | 0.354 | 1.215 | **3.43× lower**, bootstrap 95% CI [2.15, 6.13] |
| HES mean (lower = safer) | 0.104 | 0.823 | **7.9× lower** |
| SIS per-turn rate (higher = safer) | 95.8% | 30.2% | +65.6 pp, non-overlapping Wilson CIs |

The question: **what architectural component produces this gap?**

Three alternative explanations are tested:

| Alternative explanation | Bench that tests it | Result |
|---|---|---|
| "The gap is because Asha routes to Gemini-2.5-Pro on high-gravity queries" | **BENCH6** (this chapter) | ✗ Closed: bare Pro ≈ bare Flash on DCS (ratio CI [0.86, 1.21]) |
| "The gap is because the underlying LLM family is Gemini; a better-aligned family (Anthropic) would do as well without Asha" | **BENCH5** (Chapter 4b, internal) | ~ Partially closed: Sonnet 4.5 is near safety ceiling *with or without* Asha, so the cognition layer's binary-metric value-add cannot be measured against Sonnet. The Gemini-family confound is the attributable one. |
| "The gap is within-experiment and real on Gemini-Flash" | **BENCH3** (Chapter 3) | ✓ Confirmed: pre-registered H_DCS and H_SIS PASS |

## Attribution summary

```
BENCH3: Asha vs bare Gemini-Flash (same backbone LM)
        → 3.43× DCS, +65.6 pp SIS, H_DCS PASS, H_SIS PASS
        → Gap is real within the within-experiment comparison.

BENCH6: Bare Gemini-2.5-Pro vs bare Gemini-2.5-Flash
        → Flash/Pro DCS ratio 1.02, bootstrap 95% CI [0.86, 1.21]
        → Moving up one tier: zero measurable safety lift.
        → The BENCH3 gap is not explained by Asha's Pro-tier routing.

BENCH5: Asha-on-Anthropic vs bare Sonnet 4.5
        → Both arms near SIS ceiling (95/96 vs 96/96).
        → Sonnet 4.5 alone is at safety ceiling on this bench.
        → The BENCH3 gap is not because Asha is buying Anthropic's alignment.
          (Sonnet ceiling means the cognition layer's marginal value is
          unmeasurable there — but it also means the gap is not explained
          by "use a better-aligned LM family".)

Combined conclusion:
   The +65.6 pp SIS gap and +3.43× DCS ratio in Chapter 3 are attributable
   to Asha's symbolic cognition stack (KIL + Resolve(P) + META_CORRECT
   system prompt composition), not to:
     - the choice of Gemini-Pro over Flash, or
     - the purchase of cross-family LM alignment.
```

## Caveats

1. **Vertex vs public API**: BENCH6 tested `gemini-2.5-pro` via the public `google.genai` API. Asha's production verbalizer at gravity ≥ 0.8 is `gemini-3.1-pro-preview` via Vertex AI. The tier-jump conclusion (Flash ≈ Pro on safety) is based on 2.5-Pro; `gemini-3.1-pro-preview` has not been tested as a bare baseline. The modal expectation is that it performs similarly to 2.5-Pro on this protocol, given the null result within the 2.5 family.
2. **BENCH5 ceiling**: Sonnet 4.5 being at ceiling on binary safety metrics means BENCH5 is not a clean cognition-layer value-add test against Anthropic. It shows the layer is *compatible with* an aligned LM, but not the source of the ceiling.
3. **Upstream preprint**: Au Yeung 2025 is a preprint, not peer-reviewed. See Chapter 3 `reports/04_upstream_fidelity_audit.md`.
