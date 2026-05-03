# Asha — Medical Intelligence by DNAi Systems

**Evidence-grounded medical AI, accessible via the [A2A protocol](https://a2aproject.github.io/A2A/).**

Asha is a fiduciary medical AI agent backed by ~87M medical-domain knowledge vectors — a curated slice of the larger Citadel corpus (121M+ vectors across ~591 collections covering medicine, pharmacology, research literature, clinical guidelines, and structured codings). Every response includes structured provenance — source collections, evidence count, and predicate classification — so you can verify what grounded the answer.

Built by physician co-founders. Patent allowed: US 19/290,471.

## Agent Card

Live at:
```
https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
```

Fleet discovery (all 11 public agents in one card):
```
https://api.askasha.org/.well-known/agent-card.json
```

A copy of Asha's card is included in this repo at [`agent-card.json`](agent-card.json).

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
| `POST /a2a/v1/message:send` | Implemented |
| `GET /a2a/v1/tasks/{id}` | Implemented |
| `GET /a2a/v1/tasks` (list, paginated, scoped to caller) | Implemented |
| `POST /a2a/v1/tasks/{id}:cancel` | Implemented |
| `GET /a2a/v1/health` (503 when unhealthy) | Implemented |
| Bearer auth with `securitySchemes` | Implemented |
| `A2A-Version: 1.0` response header | Implemented |
| Task state lifecycle | SUBMITTED, WORKING, COMPLETED, FAILED, CANCELED |
| Task scoping to caller | Implemented (v1.0 §4.3) |

## Evaluating Asha against your current medical AI

Already on UpToDate, OpenEvidence, Glass, an OpenAI-compatible internal stack, or anything else? Here is a 30-minute, no-credit-card, side-by-side test.

### What makes this different from a typical LLM bake-off

Asha returns **structured provenance** with every response. That means you can compare not just the prose, but the actual epistemic substrate behind it. Most general-purpose APIs do not let you see this.

| Dimension | Asha returns | Typical chat API returns |
|-----------|--------------|--------------------------|
| Source collections that grounded the answer | Yes (`provenance.sources`) | No |
| Count of evidence items used | Yes (`provenance.evidence_count`) | No |
| Predicate scope (medical_general, drug, guideline, etc.) | Yes (`provenance.predicate_scope`) | No |
| Verifiable fiduciary contract hash | Yes (`provenance.contract_hash`) | No |
| Independent claim falsification | Yes (`POST /api/feng/falsify`, see [feng-a2a](https://github.com/EndlessRay/feng-a2a)) | No |

### The 5-step protocol

1. **Get a free key (no credit card, 50 queries / month).**
   ```bash
   curl -X POST https://api.askasha.org/api/a2a/signup \
     -H "Content-Type: application/json" \
     -d '{"email":"you@example.com","name":"Your Name","tier":"free"}'
   ```

2. **Pick a representative evaluation set.** 20–50 questions from your real query log. Mix easy (drug MoA, guideline lookup), medium (clinical guidelines, contraindication chains), and hard (multi-system differentials, edge-case interactions). Include questions you have seen your current provider hallucinate on. A starter is at [`examples/eval_set.txt`](examples/eval_set.txt).

3. **Run the parallel harness** at [`examples/evaluation.py`](examples/evaluation.py). Edit `query_other_api()` to match your current provider's auth + body format (most are OpenAI-compatible chat completions; if so, set `OTHER_API_BASE` and `OTHER_API_KEY` and you're done).
   ```bash
   ASHA_API_KEY=ak_...        \
   OTHER_API_BASE=https://your-current-api  \
   OTHER_API_KEY=...          \
   EVAL_SET=examples/eval_set.txt \
     python examples/evaluation.py
   ```
   Output: `ab_results_<timestamp>.json` with both providers side-by-side per question, plus latency p50/p95 and Asha evidence-count distribution.

4. **Score the dimensions that matter.** Most teams care about some subset of:

   | Dimension | How to score |
   |-----------|--------------|
   | Factual accuracy | Manual review against an authoritative reference (UpToDate, primary literature) |
   | Citation quality | Asha returns `sources` and `evidence_count` directly. For other providers, parse cited references and verify they exist (some APIs hallucinate citations). |
   | Hallucination rate | Per response, count fabricated drug names, dosing claims, made-up guidelines. Asha's pre-generation suppression + post-generation verification is designed to drive this to zero on grounded queries. |
   | Latency p50 / p95 | Auto-collected by the harness |
   | Cost at expected volume | Asha is flat-rate metered ($0 / $49 / $199 / Custom — see Pricing). Compare against per-call or per-token billing on your current provider. |
   | Auditability | Can you re-derive *what knowledge grounded the answer*, weeks later, after the model has updated? Asha: yes (contract hash + sources are stable per response). Most: no. |

5. **Stress-test any specific claim with FENG.** If either provider says something high-stakes (e.g. "Drug X is contraindicated with Drug Y"), run that exact claim through the [FENG](https://github.com/EndlessRay/feng-a2a) endpoint. You'll get a verdict — `FALSIFIED`, `WEAKENED`, `CONDITIONAL`, or `UNFALSIFIED` — with E-value, evidence-for, evidence-against, and the collections searched. This is the deepest single audit step available across any medical AI vendor today.

### What we tell evaluators honestly

- **Asha is strong on:** drug pharmacology, drug-drug interactions, clinical guidelines, evidence synthesis, anything where citation fidelity matters more than chatty bedside manner.
- **Asha is intentionally conservative on:** definitive diagnosis, medication dosing, anything that requires a licensed clinician's judgment. The fiduciary medical contract refuses to fabricate any of those rather than guess. If your current provider gives confident definitive diagnoses on demand, that is a difference, not a defect — measure hallucination rate before treating it as a feature.
- **Latency:** retrieval-augmented generation across 87M+ medical vectors is not free. Expect a few seconds end-to-end. The harness will surface exact p50/p95 numbers for your set so you can weigh the trade-off explicitly.

### Migration path if you decide to switch

- The A2A surface is bearer-auth + JSON. Most teams swap the URL and Authorization header and ship.
- Run a 2-week shadow window: route real production queries to both, log both responses, review divergences. The harness's output JSON is shaped for exactly this.
- Keep your current API as a fallback; rotate Asha keys with `POST /api/a2a/rotate-key` if a key is ever leaked.
- For high-volume production deployments, contact us via [dnai.systems](https://dnai.systems) for an Enterprise tier with custom limits and SLAs.

## Connect to Google Gemini Enterprise

Asha (and any of the 11 DNAi agents) registers as a "Custom agent via A2A" inside a Google Gemini Enterprise app. Once registered, the agent shows up to your end users in the Gemini Enterprise web app and Gemini composer surfaces.

The agent card in this repo (`agent-card.json`) is shaped to be **maximally compatible** with the Gemini Enterprise registration parser: it carries both the A2A v1.0 `supportedInterfaces[]` shape AND the flatter top-level `url` + `protocolVersion` fields used by the Gemini Enterprise console example, plus `iconUrl` and `documentationUrl`.

### Console (recommended)

1. In the Google Cloud console, open **Gemini Enterprise** → click your app → **Agents** → **Add Agents**.
2. In **Choose an agent type**, pick **Add → Custom agent via A2A**.
3. Paste the contents of [`agent-card.json`](agent-card.json) into the **Agent card JSON** field.
4. Click **Preview agent details → Next**.
5. If your users will need Asha to access Google Cloud resources on their behalf (Drive, Docs, BigQuery, etc.), add the OAuth client credentials. Otherwise click **Skip & Finish**. Asha itself does not require Google OAuth — it authenticates with its own DNAi-issued API key (Bearer auth, declared in `securitySchemes`).

### REST

If you'd rather automate it:

```bash
PROJECT_ID=your-gcp-project
LOCATION=global       # or us, eu
APP_ID=your-gemini-enterprise-app-id
ENDPOINT=${LOCATION}-discoveryengine.googleapis.com

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${ENDPOINT}/v1alpha/projects/${PROJECT_ID}/locations/${LOCATION}/collections/default_collection/engines/${APP_ID}/assistants/default_assistant/agents" \
  -d @- <<EOF
{
  "name": "asha-dnai",
  "displayName": "Asha (DNAi)",
  "description": "Fiduciary medical intelligence with verifiable provenance.",
  "a2aAgentDefinition": {
    "jsonAgentCard": $(cat agent-card.json | jq -c . | jq -R .)
  }
}
EOF
```

That single command embeds Asha's agent card into the Gemini Enterprise registration request. Replace `asha` in the agent-card URL / `agent_id` metadata to register any of the other DNAi agents (Harley, Artha, Sage, Polymath, Lyra, Leo, Mira, Ren, Arohi, Ray).

### What Gemini Enterprise users will see

- Asha appears in their Gemini Enterprise app's agent list with the icon at `https://dnai.systems/asha-logo.svg`.
- Queries route through Gemini's UI to `https://api.askasha.org/a2a/v1/message:send` over the A2A v1.0 protocol.
- Responses include the same structured provenance (sources, evidence count, contract hash) Gemini Enterprise users would see calling Asha directly.
- Authentication: Asha's own Bearer API key (per the `securitySchemes.bearer` declaration). Each registering org provisions its own key via `POST /api/a2a/signup`.

### Security notes (per Google's docs)

- Gemini Enterprise's Model Armor settings in the Cloud console **do not** automatically protect A2A agents. If you want Model Armor on top of Asha's existing fiduciary medical contract, add it via the Model Armor REST API in your registering app.
- Asha already enforces a fiduciary medical contract (no prescribing, no definitive diagnoses, jailbreak detection, contract hash on every response) at the API boundary, independent of Gemini Enterprise.
- API keys live in your environment, never in the registered agent card. Rotate any time with `POST /api/a2a/rotate-key`.

## Account & Operations Endpoints

In addition to the A2A protocol surface, Asha exposes operator endpoints for managing your API key and verifying corpus state:

| Endpoint | Method | Purpose |
|---------|--------|---------|
| `POST /api/a2a/signup` | None | Self-service API key provisioning |
| `GET /api/a2a/usage` | API key | Daily/monthly usage counters and limits |
| `POST /api/a2a/upgrade` | API key | Stripe checkout for tier upgrade |
| `GET /api/a2a/portal` | API key | Stripe Customer Portal (billing self-service) |
| `POST /api/a2a/rotate-key` | API key | Rotate (regenerate) your API key |
| `GET /api/audit/corpus-state` | JWT | Cryptographic corpus commitment (verifiable knowledge state) |
| `POST /api/feng/falsify` | JWT | Popperian claim falsification — see [feng-a2a](https://github.com/EndlessRay/feng-a2a) |

## Knowledge Coverage (Asha's slice)

Asha is the medical-intelligence agent. It is bound to medical, clinical, pharmacology, and research collections from the Citadel corpus:

| Category | Vectors | Key Sources |
|----------|---------|-------------|
| Research & Academic | ~90M | OpenAlex top-cited (16.5M), PubMed abstracts (5.1M), PMC full-text cited (5.2M), `pkg2_abstracts` (48M) |
| Medical & Clinical | ~18M | Wikidata medical (10.9M), DailyMed drug labels (889K), StatPearls clinical (76K) |
| Pharmacology | ~928K | DailyMed drug labels, FDA drug labels |
| Coding & Classification | ~304K | ICD-10, structured medical codes |

Total Citadel corpus across all 11 public agents: **121M+ vectors across ~591 live collections** (audited 2026-05-01).

## Safety

- Fiduciary medical contract enforced on every query
- Never prescribes medications or provides dosing
- Never gives definitive diagnoses
- Emergency escalation for urgent clinical scenarios
- Jailbreak detection at the API boundary
- Every response carries a verifiable contract hash

## Pricing

| Tier | Monthly | Daily Cap | Monthly Cap | Get Started |
|------|---------|-----------|-------------|-------------|
| Free | $0 | 10 queries | 50 queries | `POST /api/a2a/signup` |
| Developer | $49 | 200 queries | 1,000 queries | `POST /api/a2a/upgrade` |
| Pro | $199 | 2,000 queries | 10,000 queries | `POST /api/a2a/upgrade` |
| Enterprise | Custom | Unlimited | Unlimited | [dnai.systems](https://dnai.systems) |

## Other DNAi Agents

Asha is one of 11 public agents in the DNAi fleet. All agents share the same base URL (`https://api.askasha.org`), auth system, and A2A protocol surface. The `agent_id` in metadata selects which agent handles your query.

| Agent | Domain | Repo | Agent Card |
|-------|--------|------|------------|
| **Asha** | Medical intelligence | [asha-a2a](https://github.com/EndlessRay/asha-a2a) | `?agent_id=asha` |
| **Harley** | Fitness coaching | [harley-a2a](https://github.com/EndlessRay/harley-a2a) | `?agent_id=harley` |
| **Artha** | Financial analysis | [artha-a2a](https://github.com/EndlessRay/artha-a2a) | `?agent_id=artha` |
| **Sage** | Nutrition & wellness | [sage-a2a](https://github.com/EndlessRay/sage-a2a) | `?agent_id=sage` |
| **Polymath** | Math & science | [polymath-a2a](https://github.com/EndlessRay/polymath-a2a) | `?agent_id=polymath` |
| **Lyra** | Medical research | — | `?agent_id=lyra` |
| **Leo** | Legal aid | — | `?agent_id=leo` |
| **Mira** | Marketing & growth | — | `?agent_id=mira` |
| **Ren** | Customer support | — | `?agent_id=ren` |
| **Arohi** | Practice management | — | `?agent_id=arohi` |
| **Ray** | Platform architecture | — | `?agent_id=ray` |

Companion services:

| Service | Repo | Purpose |
|---------|------|---------|
| FENG (Falsification Engine) | [feng-a2a](https://github.com/EndlessRay/feng-a2a) | Popperian claim falsification with E-value scoring |

## Links

- **Agent Card**: https://api.askasha.org/.well-known/agent-card.json?agent_id=asha
- **Fleet Card**: https://api.askasha.org/.well-known/agent-card.json
- **Product**: https://askasha.org
- **Company**: https://dnai.systems
- **A2A Protocol**: https://a2aproject.github.io/A2A/

## License

The A2A interface specification and examples in this repository are available under the [MIT License](LICENSE). The underlying Asha engine, knowledge collections, CIU architecture, and proprietary systems are not open source.
