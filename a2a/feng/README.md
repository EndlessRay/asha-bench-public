# FENG — Falsification Engine by DNAi Systems

**Popperian claim falsification as an API. No other agent offers this.**

Submit any natural-language claim. FENG runs forward search (supporting evidence), inverse search (contradicting evidence via vector negation), semantic negation, and computes an E-value statistical verdict against the Citadel corpus (121M+ vectors across ~591 collections — medical, scientific, financial, and general knowledge).

Verdicts: **FALSIFIED** | **WEAKENED** | **CONDITIONAL** | **UNFALSIFIED**

## Endpoint
```
POST https://api.askasha.org/api/feng/falsify
Authorization: Bearer <jwt>
Content-Type: application/json

{"claim": "Metformin is first-line for type 2 diabetes", "k": 10}
```

## Response
```json
{
  "verdict": "UNFALSIFIED",
  "e_value": 47.3,
  "evidence_for": [...],
  "evidence_against": [...],
  "confidence": 8.5,
  "collections_searched": ["statpearls_clinical", "pubmed_abstracts", "openalex_top_cited"]
}
```

## How It Works
1. Embeds the claim as a 1024d vector
2. Forward search: supporting evidence across medical/scientific/financial collections
3. Inverse search: negates the vector, finds contradictions
4. Semantic negation: "evidence against {claim}"
5. E-value: likelihood ratio (E > 20 = validated, E < 0.05 = falsified, in-between = WEAKENED or CONDITIONAL)

## Companion to the DNAi Agent Fleet

FENG is the falsification primitive that powers epistemic checks behind every public DNAi agent. The same engine is exposed publicly at the endpoint above so external A2A clients can stress-test claims independently.

Part of 11 public agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only — engine, embeddings, and corpus are proprietary).
