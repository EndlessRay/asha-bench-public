# Sage — Nutrition & Wellness by DNAi Systems

**AI nutrition and wellness agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Evidence-grounded nutrition guidance, gut-brain axis insights, therapeutic wellness. Named for both the wise elder and the healing herb.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=sage
```

## Skills
| Skill | Description |
|-------|-------------|
| Nutrition Analysis | Macro/micronutrient analysis, dietary planning |
| Food Interaction | Food-drug and food-nutrient interaction checking |
| Wellness Assessment | Holistic wellness with ancestral wisdom |
| Gut Health | Gut-brain axis science and microbiome guidance |

## Quick Start
```bash
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"How much protein should a 180lb male eat daily?"}]},"metadata":{"agent_id":"sage"}}'
```

Part of 11 agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only).
