# Harley — Fitness Coaching by DNAi Systems

**AI fitness coaching agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Designs workouts, analyzes exercise science, coaches clients.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=harley
```

## Skills
| Skill | Description |
|-------|-------------|
| Workout Design | Push-pull-legs, powerlifting, hypertrophy programming |
| Exercise Lookup | Exercise database with muscles, equipment, progressions |
| Nutrition Coaching | Macro targets and meal planning |
| Program Builder | Periodized programs with deloads and RPE targets |

## Quick Start
```bash
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"Design a 4-day push-pull-legs split"}]},"metadata":{"agent_id":"harley"}}'
```

Part of 11 agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only).
