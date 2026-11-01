# Project summary — P5 Agentic Platform Probe

**Snapshot date:** 2026-10-31  
**Workspace:** `p5_agentic`  
**Status:** **E1 frozen** 2026-08-20; **E2 frozen** 2026-08-23; **E3 deployed and tested** 2026-10-31 (happy, fail, idempotent retry). Two follow-ons are written and **not started**.

> Living specs: [docs/E1.md](docs/E1.md), [docs/E2.md](docs/E2.md), [docs/E3.md](docs/E3.md), public [README.md](README.md), operator guide [docs/how-to/setup-run-deploy.md](docs/how-to/setup-run-deploy.md). This file is the **portfolio / LLM context** snapshot (parallel to the P0–P3 notes).

---

## What this project is for

**Portfolio P5**: a short, freezeable probe of MarTech-shaped **agentic platform** work. Domain vocabulary is illustrative. The repo is not a production marketing platform.

### Portfolio emphasis (what to claim)

- **Tool-using agent** over a fake marketing-ops workflow (E1): brief + segment stub, stub tools, one journey step, constraint check before any side effect.
- **Thin RAG** over a fixed corpus (E2): lexical retrieve, cite, or fail closed.
- **Cloud reliability floor** around that RAG call (E3): HTTP API, Lambda, DynamoDB idempotency, deployed and tested.
- **Engineering practices carried forward** from earlier portfolio work: charter, freeze/defer lists, contracts-first slices, smoke where cheap.

### Honest portfolio value (what not to oversell)

| Signal | Reality in this snapshot |
|--------|--------------------------|
| Agents | One explicit tool loop, four stub tools, one journey step. No activation, no multi-step journey graph |
| RAG | Lexical keyword overlap over three markdown files. No embeddings, no vector store |
| Cloud | SAM API + Lambda + DynamoDB. Happy, fail, and idempotent retry verified on the deployed API |
| Evals | Proposed only. The CLIs check `status` on two paths |
| Bedrock | Proposed only. Generation is xAI |

**One-line portfolio read:** an illustrative **agent → grounded Q&A → idempotent API** tracer for agentic platform work — not a production MarTech system and not a model-training project.

---

## Relationship to P0–P3

| Project | Primary signal |
|---------|----------------|
| **P0** | Event-driven AWS serverless middleware |
| **P1** | Orchestration + failure taxonomy |
| **P2** | Anomaly monitoring + operator SPA |
| **P3** | C++/ROS edge → thin AWS (v1 frozen) |
| **P5** | **Agentic AI probe (MarTech-shaped)** |

**Reuse:** charter discipline, freeze/defer lists, contracts-first thinking, smoke where cheap.  
**Do not reuse:** order/retail domain as the story; another monitoring SPA as the hero; the robotics/C++ path.

---

## Tech stack (locked)

| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ (Lambda runtime in `template.yaml` is 3.13) |
| Agent / RAG framework | **LangChain** |
| LLM | **xAI Grok** via `langchain-xai` (`XAI_API_KEY`). Default model `grok-3-fast` |
| E1 | Explicit `bind_tools` loop. Stub segment and rules under `e1/fixtures/` |
| E2 retrieval | Lexical keyword overlap. `MIN_SCORE = 2`. Corpus in `e2/corpus/` |
| E2 generation | Grounded prompt; `status` `answered` or `unknown` |
| E3 cloud | AWS SAM, API Gateway HTTP API, Lambda, DynamoDB (`idempotency_key`). Region in `samconfig.toml`: `us-east-1`, stack `p5-e3-rag` |
| Secrets | `.env` locally; `XaiApiKey` parameter on deploy. Never committed |

Embeddings, LlamaIndex, Google ADK, and a vector database are deferred. The cite / fail-closed contract was written so a later retrieval swap does not change the JSON.

---

## End-to-end flow (shipped)

```text
E1  brief + segment id
      → ChatXAI tool loop (get_segment, get_audience_rules,
         propose_journey_step, validate_constraints)
      → structured JSON: proposal, validation, status

E2  query
      → chunk markdown → lexical retrieve
      → score < MIN_SCORE → status unknown (no model call)
      → else grounded generation + citations → status answered

E3  POST /ask { query, idempotency_key }
      → DynamoDB get
      → hit: return stored E2 JSON (cache.hit true)
      → miss: e2.rag.answer_query → put item → cache.hit false
```

E1 and E2 run as local CLIs (`python -m e1.run`, `python -m e2.run`). E3 wraps **E2 only**. It does not host the E1 agent loop.

---

## Experiment history (what shipped)

| ID | Focus | Outcome |
|----|--------|---------|
| **E1** | Tool-using agent | **Frozen** 2026-08-20. Happy path (allowed channel) and fail path (SMS proposed, constraint rejected) verified |
| **E2** | Thin RAG | **Frozen** 2026-08-23. In-corpus question cites; out-of-corpus question returns `unknown` |
| **E3** | Idempotent RAG API | **Deployed and tested** 2026-10-31. Happy path, fail path (`unknown`), and idempotent retry on the live API |

---

## Engineering capabilities demonstrated

1. **Judgment about where an LLM belongs** — draft a journey step with the model; validate constraints in code. Retrieve with a score gate; generate only when evidence clears it.
2. **Tool orchestration** — explicit tool loop, stub platform tools, structured result assembled from tool output.
3. **Grounded answers** — fixed corpus, citations, fail closed when retrieval or the model refuses.
4. **Thin AWS floor** — synchronous HTTP API, DynamoDB idempotency so a retry does not call the model again. Deployed and tested.
5. **Portfolio process** — slice specs, freeze notes, anonymous public docs, proposals kept out of the frozen slices.

---

## Intentionally NOT built

- Adobe Experience Platform, Journey Optimizer, or AEM
- Production vector search, embeddings, or a hybrid-search product
- Multi-step journey graphs, activation, or sending messages
- Auth, multi-tenant IAM, Kubernetes, Step Functions, or an async job API
- P0-parity observability, multi-stage CD, or an operator SPA
- Model training or fine-tuning
- An eval harness or a second model provider (both proposed; see below)

---

## Current state (2026-10-31)

- **E1 and E2 are frozen.** Do not change prompts, `MIN_SCORE`, chunking, or the agent loop unless that slice is explicitly reopened.
- **E3 is deployed and tested:** happy path, fail path (`status: unknown`), and an idempotent retry on the live API.
- **Demoable today:** `python -m e1.run --path happy|fail`, `python -m e2.run --path happy|fail`, and `POST /ask` (see [docs/how-to/bruno-e3.md](docs/how-to/bruno-e3.md)).
- **Next move is a deliberate pick.** The proposals below are not implied work.

---

## Possible later extensions

Sources: [docs/planning/e3-bedrock.md](docs/planning/e3-bedrock.md), [docs/planning/e4-evals.md](docs/planning/e4-evals.md). Neither is started. Freeze E3 on the xAI path before starting either.

| Direction | Kind | What it is | What it does not change |
|-----------|------|------------|-------------------------|
| **Bedrock generation** | E3 follow-on, not a new experiment | Converse behind the E3 Lambda. Credential becomes `bedrock:InvokeModel` on the function role. Default CLI stays `ChatXAI`. Needs a small generation seam in `e2.rag.answer_query` because that function constructs the xAI client itself | Retrieval, corpus, `MIN_SCORE`, cite / refuse JSON, `POST /ask` shape. E3.1 (async E1 API, already reserved in [docs/E3.md](docs/E3.md)) stays a different idea |
| **E4 eval harness** | New experiment | Golden JSONL cases over frozen E2. Retrieval layer calls `retrieve` only (no API spend). Generation layer calls `answer_query` and checks `status`, citation path, and a few answer strings. Exit `2` on failure | Do not "fix" a failing case by editing `e2/rag.py`. Do not call `POST /ask` — the idempotency cache would replay the first answer. No LLM-as-judge, RAGAS, DeepEval, or LangSmith in v1 |

Out of both proposals: Knowledge Bases, Bedrock Agents, Guardrails, embeddings, and hosted model-evaluation jobs. Those replace the lexical gate or the E1 tool loop instead of demonstrating the contract already in the repo.

---

## Bottom line

P5 is a **probe with three shipped slices**. E1 drafts one governed journey step. E2 cites or refuses. E3 serves that answer behind an idempotent API. Bedrock and evals are named follow-ons, written down so they are not forgotten and not started by accident.

---

## How to use this with the next LLM

1. **E1 and E2 stay frozen** unless the user explicitly reopens them.
2. **E3 is deployed and tested.** Do not reopen it unless asked.
3. **Do not implement** [docs/planning/e3-bedrock.md](docs/planning/e3-bedrock.md) or [docs/planning/e4-evals.md](docs/planning/e4-evals.md) unless asked.
4. Stay anonymous in `docs/`, README, code, and this file. Private steering stays in `.cursor/internal/`, which is gitignored.
5. Stack stays LangChain + xAI for the frozen CLIs. E3 is SAM + Lambda + API Gateway + DynamoDB. Keep secrets out of the repo.
