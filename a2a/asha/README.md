# Asha — Medical Intelligence by DNAi Systems

**Evidence-grounded medical AI, accessible via the A2A protocol.**

Asha is a fiduciary medical AI agent built on 121M vectors across 530 curated knowledge collections. She answers clinical questions with structured provenance — every response tells you exactly which collections contributed evidence, how many items were retrieved, and which citations back the answer.

Built by two physician co-founders: **Deepan Singh, MD, FAPA** (board-certified psychiatrist) and **Paridhi Anand, MD**.

> **Patent allowed:** US 19/290,471

## Agent Card

```
https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
```

## A2A Skills

| Skill | Description |
|-------|-------------|
| **Medical Q&A** | Differential diagnosis, lab interpretation, comorbidity management, mechanism of action queries |
| **Drug Interaction Check** | Polypharmacy safety evaluation using DailyMed and FDA drug label data |
| **Clinical Guideline Lookup** | ADA, USPSTF, AHA, WHO guidelines with citation support |
| **Evidence Synthesis** | Multi-source literature synthesis across PubMed, OpenAlex, StatPearls |

## Quick Start

### Python

```python
import requests

response = requests.post(
    "https://api.askasha.org/a2a/v1/message:send",
    headers={
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json",
    },
    json={
        "message": {
            "role": "user",
            "parts": [{"text": "What are the interactions between warfarin and amiodarone?"}],
        },
        "metadata": {"agent_id": "asha"},
    },
)

task = response.json()["task"]
print(f"Status: {task['status']['state']}")

# Response text
for artifact in task["artifacts"]:
    if artifact["name"] == "response":
        print(artifact["parts"][0]["text"])

# Provenance metadata
for artifact in task["artifacts"]:
    if artifact["name"] == "provenance":
        provenance = artifact["parts"][0]["data"]
        print(f"Sources: {provenance['sources']}")
        print(f"Evidence count: {provenance['evidence_count']}")
        print(f"Model: {provenance['model']}")
        print(f"Contract hash: {provenance['contract_hash']}")
```

### curl

```bash
curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "role": "user",
      "parts": [{"text": "What is the mechanism of action of metformin?"}]
    },
    "metadata": {"agent_id": "asha"}
  }'
```

## Knowledge Collections

Asha draws from 530 Qdrant collections totaling 121M vectors:

| Category | Collections | Vectors | Key Sources |
|----------|-------------|---------|-------------|
| Research & Academic | ~40 | ~90M | OpenAlex (16.5M), PubMed (5.1M), PMC full-text (5.2M) |
| Medical & Clinical | ~70 | ~18M | Wikidata medical (10.9M), DailyMed drug labels (889K), StatPearls (76K) |
| Health & Public | ~10 | ~3M | OpenFoodFacts nutrition, CDC guidelines, USDA food data |

## Response Format

Every A2A response includes two artifacts:

### 1. Response Artifact
The clinical answer with inline citations, medical disclaimers, and emergency escalation flags.

### 2. Provenance Artifact
Structured metadata for auditability:

```json
{
  "sources": ["pubmed_abstracts", "dailymed_drug_labels", "clinical_guidelines"],
  "evidence_count": 48,
  "citations": ["PMID:31167558", "..."],
  "contract_hash": "2060c8d4f4d15454",
  "predicate_scope": ["medical_general"],
  "model": "claude-opus-4-6"
}
```

## Safety Architecture

- Fiduciary medical contract enforced on every response (contract hash auditable)
- Never prescribes medications or provides dosing
- Never gives definitive diagnoses
- Never fabricates citations or PMIDs
- Emergency escalation for urgent clinical scenarios
- Jailbreak detection at the A2A API boundary

## Protocol

| Spec | Value |
|------|-------|
| Protocol | A2A v1.0 |
| Transport | HTTP+JSON |
| Auth | Bearer API key |
| Rate limit | 60 requests/minute |
| Task store | PostgreSQL-backed with audit trail |
| Enterprise model | Claude Opus 4.6 |
| Consumer model | Claude Haiku 4.5 |

## API Access

Request an API key: **agents@dnai.systems**

## Links

- **Agent card**: https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
- **Consumer app**: https://askasha.org
- **Company**: https://dnai.systems

## License

The A2A interface specification and examples in this repository are available under the MIT License. The underlying Asha engine, knowledge collections, and proprietary systems are not open source.
