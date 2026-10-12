# Sage — Nutrition & Wellness by DNAi Systems

**AI nutrition and wellness agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Evidence-grounded nutrition guidance, gut-brain axis insights, therapeutic wellness. Named for both the wise elder and the healing herb (Salvia officinalis).

Backed by ~51M nutrition, wellness, and traditional-knowledge vectors (USDA FoodData Central, OpenFoodFacts global, herbal pharmacopoeia, gut-brain microbiome literature) drawn from the Citadel corpus.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=sage
```

A copy is included in this repo at [`agent-card.json`](agent-card.json).

## Skills
| ID | Skill | Description |
|----|-------|-------------|
| `nutrition-analysis` | Nutrition Analysis | Macro/micronutrient analysis, dietary planning |
| `food-interaction` | Food-Drug Interaction | Food-drug interactions, nutrient depletions |
| `wellness-assessment` | Wellness Assessment | Holistic wellness with ancestral wisdom |
| `gut-health` | Gut-Brain Axis Analysis | Microbiome science, prebiotic/probiotic guidance |

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
  -d '{"message":{"role":"user","parts":[{"text":"How much protein should a 180lb male eat daily?"}]},"metadata":{"agent_id":"sage"}}'
```

## Connect to Google Gemini Enterprise

Sage registers as a "Custom agent via A2A" inside any Google Gemini Enterprise app. Paste this repo's [`agent-card.json`](agent-card.json) into **Gemini Enterprise → your app → Agents → Add Agents → Custom agent via A2A** and click through. The card carries both the A2A v1.0 `supportedInterfaces[]` shape AND top-level `url` / `protocolVersion` / `iconUrl` / `documentationUrl` for maximum parser compatibility. Full step-by-step in [asha-a2a → Connect to Google Gemini Enterprise](https://github.com/EndlessRay/asha-a2a#connect-to-google-gemini-enterprise).

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
