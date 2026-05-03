# Polymath — Math & Science by DNAi Systems

**AI mathematical and scientific verification agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Verifies proofs, checks statistical claims, explains scientific concepts, synthesizes cross-domain knowledge. Truth Through Proof — the Renaissance ideal of mastery across all domains.

Backed by ~17M mathematics and science vectors (mathematics textbooks, arXiv multidomain, science & technology canon, OpenAlex top-cited literature, ConceptNet commonsense) drawn from the Citadel corpus.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=polymath
```

A copy is included in this repo at [`agent-card.json`](agent-card.json).

## Skills
| ID | Skill | Description |
|----|-------|-------------|
| `proof-verification` | Proof Verification | Mathematical proof checking and validation |
| `statistical-check` | Statistical Analysis Check | Methodology audit, sample size, p-value interpretation |
| `scientific-explanation` | Scientific Explanation | Physics, chemistry, biology with mathematical rigor |
| `cross-domain-synthesis` | Cross-Domain Synthesis | Multi-domain knowledge synthesis |

## Quick Start
```bash
# 1. Get a free API key
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

# 2. Send a query
curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"Prove that the square root of 2 is irrational"}]},"metadata":{"agent_id":"polymath"}}'
```

## Connect to Google Gemini Enterprise

Polymath registers as a "Custom agent via A2A" inside any Google Gemini Enterprise app. Paste this repo's [`agent-card.json`](agent-card.json) into **Gemini Enterprise → your app → Agents → Add Agents → Custom agent via A2A** and click through. The card carries both the A2A v1.0 `supportedInterfaces[]` shape AND top-level `url` / `protocolVersion` / `iconUrl` / `documentationUrl` for maximum parser compatibility. Full step-by-step in [asha-a2a → Connect to Google Gemini Enterprise](https://github.com/EndlessRay/asha-a2a#connect-to-google-gemini-enterprise).

## A2A Surface

Bearer-auth A2A v1.0 endpoints, identical across all DNAi agents — only the `agent_id` changes:

| Endpoint | Purpose |
|---------|---------|
| `POST /a2a/v1/message:send` | Send a query, receive a Task |
| `GET /a2a/v1/tasks/{id}` | Poll task state and fetch artifacts |
| `GET /a2a/v1/tasks` | List recent tasks (scoped to caller) |
| `POST /a2a/v1/tasks/{id}:cancel` | Cancel an in-flight task |
| `GET /a2a/v1/health` | Health probe |
| `POST /api/a2a/upgrade` / `GET /api/a2a/portal` | Stripe upgrade and self-service billing |
| `POST /api/a2a/rotate-key` | Rotate your API key |

## Pricing

| Tier | Monthly | Daily / Monthly Cap |
|------|---------|---------------------|
| Free | $0 | 10 / 50 |
| Developer | $49 | 200 / 1,000 |
| Pro | $199 | 2,000 / 10,000 |
| Enterprise | Custom | Unlimited |

Part of 11 public agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only — engine, knowledge collections, and architecture are proprietary).
