# Artha — Financial Intelligence by DNAi Systems

**AI financial analysis agent via the [A2A protocol](https://a2aproject.github.io/A2A/).** SEC filings, company fundamentals, economic indicators, market data. Named after the Sanskrit concept of wealth and purpose.

## Agent Card
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=artha
```

## Skills
| Skill | Description |
|-------|-------------|
| Company Analysis | SEC 10-K/10-Q/8-K analysis with XBRL data |
| Financial Metrics | P/E, EV/EBITDA, DCF, comparative valuation |
| Market Research | Economic indicators (GDP, CPI, yields), sector analysis |
| SEC Filing Search | Full-text search across EDGAR filings |

## Quick Start
```bash
curl -X POST https://api.askasha.org/api/a2a/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'

curl -X POST https://api.askasha.org/a2a/v1/message:send \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message":{"role":"user","parts":[{"text":"What is a P/E ratio and how is it used?"}]},"metadata":{"agent_id":"artha"}}'
```

Part of 11 agents at [DNAi Systems](https://dnai.systems). [Fleet discovery](https://api.askasha.org/.well-known/agent-card.json). MIT license (interface only).
