# Asha — Medical Intelligence by DNAi Systems

**Evidence-grounded medical AI, accessible via the [A2A protocol](https://a2aproject.github.io/A2A/).**

Asha is a fiduciary medical AI agent backed by 87M+ knowledge vectors across curated medical collections (PubMed, StatPearls, FDA drug labels, clinical guidelines). Every response includes structured provenance — source collections, evidence count, and predicate classification — so you can verify what grounded the answer.

Built by physician co-founders. Patent allowed: US 19/290,471.

## Agent Card

Live at:
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
```

A copy is included in this repo at [`agent-card.json`](agent-card.json).

## Skills

| Skill | ID | Description |
|-------|-----|-------------|
| Medical Q&A | `medical-qa` | Differential diagnosis, lab interpretation, mechanism of action, comorbidity management |
| Drug Interaction Check | `drug-interaction-check` | Polypharmacy safety evaluation using DailyMed and FDA drug label data |
| Clinical Guideline Lookup | `clinical-guidelines` | ADA, USPSTF, AHA, WHO guidelines with citation support |
| Evidence Synthesis | `evidence-synthesis` | Multi-source literature synthesis across PubMed, OpenAlex, StatPearls |

## Quick Start

### 1. Get an API Key

```bash
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "name": "Your Name", "tier": "free"}'
```

The response includes your API key (shown once — save it).

### 2. Send a Query

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

### 3. Parse the Response

Every response returns a Task with two artifacts:

**Response artifact** — the clinical answer with citations.

**Provenance artifact** — structured metadata:
```json
{
  "sources": ["pubmed_abstracts", "dailymed_drug_labels", "clinical_guidelines"],
  "evidence_count": 48,
  "contract_hash": "...",
  "predicate_scope": ["medical_general"]
}
```

See [`examples/python_client.py`](examples/python_client.py) for a complete Python example.

## A2A Protocol Compliance

| Requirement | Status |
|-------------|--------|
| Agent Card at `/.well-known/agent-card.json` | Served |
| `POST /message:send` | Implemented |
| `GET /tasks/{id}` | Implemented |
| `GET /tasks` (list, paginated) | Implemented |
| `POST /tasks/{id}:cancel` | Implemented |
| `GET /health` (503 when unhealthy) | Implemented |
| Bearer auth with `securitySchemes` | Implemented |
| `A2A-Version: 1.0` response header | Implemented |
| Task state lifecycle | SUBMITTED, WORKING, COMPLETED, FAILED, CANCELED |
| Task scoping to caller | Implemented (v1.0 §4.3) |

## Knowledge Collections

| Category | Vectors | Key Sources |
|----------|---------|-------------|
| Research & Academic | ~90M | OpenAlex (16.5M), PubMed (5.1M), PMC full-text (5.2M) |
| Medical & Clinical | ~18M | Wikidata medical (10.9M), DailyMed (889K), StatPearls (76K) |
| Pharmacology | ~928K | DailyMed drug labels, FDA drug labels |
| Coding & Classification | ~304K | ICD-10, medical codes |

## Safety

- Fiduciary medical contract enforced on every query
- Never prescribes medications or provides dosing
- Never gives definitive diagnoses
- Emergency escalation for urgent clinical scenarios
- Jailbreak detection at the API boundary
- Every response carries a verifiable contract hash

## Pricing

| Tier | Monthly | Queries | Get Started |
|------|---------|---------|-------------|
| Free | $0 | 50/month | `POST /api/a2a/signup` |
| Developer | $49 | 1,000/month | Upgrade via `/api/a2a/upgrade` |
| Pro | $199 | 10,000/month | Upgrade via `/api/a2a/upgrade` |
| Enterprise | Custom | Unlimited | Contact below |

## Other DNAi Agents

Asha is one of 11 public agents in the DNAi fleet:

| Agent | Domain | Agent Card |
|-------|--------|------------|
| **Asha** | Medical intelligence | This repo |
| Harley | Fitness coaching | `?agent_id=harley` |
| Artha | Financial analysis | `?agent_id=artha` |
| Sage | Nutrition & wellness | `?agent_id=sage` |
| Polymath | Math & science | `?agent_id=polymath` |
| Lyra | Medical research | `?agent_id=lyra` |
| Leo | Legal aid | `?agent_id=leo` |
| Mira | Marketing & growth | `?agent_id=mira` |
| Ren | Customer support | `?agent_id=ren` |
| Arohi | Practice management | `?agent_id=arohi` |
| Ray | Platform architecture | `?agent_id=ray` |

All agents share the same base URL and auth system. The `agent_id` in metadata selects which agent handles your query.

Fleet discovery:
```
https://api.askasha.org/.well-known/agent-card.json
```

## Links

- **Agent Card**: https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
- **Fleet Card**: https://api.askasha.org/.well-known/agent-card.json
- **Product**: https://askasha.org
- **Company**: https://dnai.systems
- **A2A Protocol**: https://a2aproject.github.io/A2A/

## License

The A2A interface specification and examples in this repository are available under the [MIT License](LICENSE). The underlying Asha engine, knowledge collections, CIU architecture, and proprietary systems are not open source.
