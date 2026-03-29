# Polymath — Math & Science by DNAi Systems

**AI mathematical and scientific verification agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** Verifies proofs, checks statistical claims, explains scientific concepts, synthesizes cross-domain knowledge. Named after the Renaissance ideal.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=polymath
```

## Skills
| Skill | Description |
|-------|-------------|
| Proof Verification | Mathematical proof checking and validation |
| Statistical Check | Statistical claim verification and methodology audit |
| Scientific Explanation | Physics, chemistry, biology concept explanation |
| Cross-Domain Synthesis | Multi-domain knowledge synthesis |

## Quick Start
```bash
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"Prove that the square root of 2 is irrational"}]},"metadata":{"agent_id":"polymath"}}'
```

Part of 11 agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only).
