# Harley — Fitness Coaching by DNAi Systems

**AI fitness coaching agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Designs workouts, analyzes exercise science, coaches clients. Backed by ~52M training/sport-science vectors from the Citadel corpus.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=harley
```

A copy is included in this repo at [`agent-card.json`](agent-card.json).

## Skills
| ID | Skill | Description |
|----|-------|-------------|
| `workout-design` | Workout Design | Push-pull-legs, powerlifting, hypertrophy programming with periodization |
| `exercise-lookup` | Exercise Lookup | Curated exercise library with muscles, equipment, progressions |
| `nutrition-coaching` | Nutrition Coaching | Macro targets, meal planning (USDA FoodData Central) |
| `client-assessment` | Client Assessment | Trend analysis on body stats, workout logs, PRs |
| `program-builder` | Program Builder | Multi-week periodized programs with deloads and RPE targets |

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
  -d '{"message":{"role":"user","parts":[{"text":"Design a 4-day push-pull-legs split"}]},"metadata":{"agent_id":"harley"}}'
```

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
