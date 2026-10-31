# P5 — Agentic Platform Probe

**Workspace:** `p5_agentic`  
**Status:** **E1 frozen** 2026-08-20; **E2 frozen** 2026-08-23; **E3 deployed and tested** 2026-10-31 (happy, fail, idempotent retry)  
**Created:** 2026-08-17  
**Related:** [docs/E1.md](docs/E1.md), [docs/E2.md](docs/E2.md), [docs/E3.md](docs/E3.md), [P5_STATUS.md](P5_STATUS.md)

Private steering (career, engagement) lives in `.cursor/internal/` and stays out of a public commit.

---

## Purpose

A **short, freezeable probe** to get a concrete feel for MarTech-shaped **agentic platform** work — tool-using agents, RAG, and a thin cloud-native reliability slice around LLM calls.

Primary reasons:

1. **Sense-check** — decide whether day-to-day agentic platform engineering is interesting work.
2. **Skill floor** — enough hands-on with Python, LangChain, LLM tools, and RAG to speak honestly about the pattern.
3. **Optional portfolio signal** — only if a slice freezes cleanly; not required for the probe to succeed.

This is **not** a multi-month portfolio saga.

---

## Non-goals

- Adobe Experience Platform / Journey Optimizer / AEM depth
- P0-parity observability, multi-stage CD, or operator SPA
- Model training, fine-tuning, or deep ML research
- Robotics / ROS / C++
- Building a real MarTech product or claiming production agent experience beyond what ships here

---

## Experiments (starting slices)

Implement **in order**. Freeze each slice before starting the next. Default timebox: **~8–12 hours per slice**.

| ID | Slice | Signal |
|----|--------|-------------|
| **E1** | **Tool-using agent** over a fake marketing-ops workflow (brief + segment stub → tools for audience rules / journey step / constraint checks) | Workflow automation + tool orchestration |
| **E2** | **Thin RAG** over a small doc corpus (rules / FAQs / runbooks) with citations; fail closed when unknown | Retrieval + grounded answers |
| **E3** | **Cloud-native reliability slice** around an LLM call (API + state + retries / idempotency) | Platforms, not notebooks |

**E1:** [frozen](docs/E1.md) — do not expand E1 scope without an explicit reopen.  
**E2:** [frozen](docs/E2.md) — do not expand E2 scope without an explicit reopen.  
**E3:** [deployed and tested](docs/E3.md) 2026-10-31 — happy, fail, and idempotent retry on the live API.

E3 implementation plan: [docs/E3.md](docs/E3.md).  
E2 implementation plan: [docs/E2.md](docs/E2.md).  
E1 implementation plan: [docs/E1.md](docs/E1.md).

---

## Stack (locked 2026-08-17; E2 adds local embeddings)

| Choice | Lock | Notes |
|--------|------|--------|
| Language | **Python 3.11+** | |
| Agent framework | **LangChain** | Google ADK / LlamaIndex deferred |
| LLM | **xAI Grok** (`langchain-xai`, `XAI_API_KEY`) | Generation for E1/E2 |
| Model | **`grok-3-fast`** (default) | Escalate to `grok-4` only if flaky |
| Embeddings (E2) | Deferred; **lexical retrieve** in scaffold | Cite / fail-closed contract unchanged; embeddings optional later |
| Cloud (E3) | Thin AWS floor acceptable | Credibility, not P0 parity |
| Domain | Illustrative MarTech vocabulary | Patterns matter more than Adobe fidelity; glossary in [docs/concepts/](docs/concepts/README.md) |

---

## Success and stop rules

The probe succeeds when the developer can answer:

> Do I want to spend years wiring LLMs into enterprise systems and owning the reliability of that glue?

| Outcome | Action |
|---------|--------|
| Clear **yes** after E1 (or E1+E2) | Optional continue E3 as portfolio depth |
| Clear **no** | Freeze; do not expand P5 |
| **Ambiguous** after E1 | Run E2 only if still cheap; then decide — do not invent E4+ |

**E1 freeze outcome (2026-08-20):** **Yes, with nuance** — interested in agentic *platform* work framed as business judgment (where LLM adds value vs rules/data), not as AI evangelism. Full note: [docs/E1.md — Success signal](docs/E1.md#freeze-note--2026-08-20).

**E2 freeze outcome (2026-08-23):** Happy + fail paths verified. Retrieve → generate → cite / refuse contract holds on lexical retrieval over a fixed corpus. Reinforces E1 stance: corpus and thresholds as invariant data; LLM for synthesis within supplied context. Full note: [docs/E2.md — Success signal](docs/E2.md#freeze-note--2026-08-23).

Hard stops: timebox overrun without a demoable path; scope creep into Adobe or a full platform rebuild.

---

## Relationship to P0–P3

| Project | Primary signal |
|---------|----------------|
| P0 | Event-driven AWS serverless middleware |
| P1 | Orchestration + failure taxonomy |
| P2 | Anomaly monitoring + SPA |
| P3 | C++/ROS edge → thin AWS (v1 frozen) |
| **P5** | **Agentic AI probe (MarTech-shaped)** |

**Reuse:** charter discipline, freeze/defer lists, contracts-first thinking, smoke where cheap.  
**Do not reuse:** order/retail domain as the story; another monitoring SPA as the hero.

---

## Documentation & disclosure

This project assumes **eventual public GitHub sharing**.

| Scope | Transparency | Examples |
|-------|----------------|----------|
| **This charter** (`P5_CHARTER.md`), `docs/`, README, code | **Anonymous** | Illustrative MarTech vocabulary only |
| **`.cursor/internal/`** | **Transparent** | Career profile, role posting, engagement log in [P5_CHARTER_INTERNAL.md](.cursor/internal/P5_CHARTER_INTERNAL.md) |

Public docs use illustrative MarTech vocabulary only — no employer names, colleague names, req IDs, or referral details. See [.cursor/rules/p5-documentation.mdc](.cursor/rules/p5-documentation.mdc) for agent enforcement.

**Before publishing:** exclude `.cursor/internal/` from the public repo.

---

## How to use this with the next LLM

1. **P5 is a probe** — prefer freezeable tracers over encyclopedic agent mastery.
2. **E1 and E2 are frozen** — do not expand either unless the user explicitly reopens them.
3. **E3 is deployed and tested.** It wraps E2 only (API + DynamoDB idempotency). Do not reopen it unless asked.
4. **Do not** expand into Adobe, full MarTech platforms, or P0-parity ops without an update to this doc.
5. Stack is locked: LangChain + xAI for LLM; E3 uses AWS SAM + Lambda + API Gateway + DynamoDB. Keep secrets out of the repo.
6. Follow [.cursor/rules/p5-documentation.mdc](.cursor/rules/p5-documentation.mdc): anonymous in this charter, `docs/`, README, and code. Private steering stays in `.cursor/internal/`.
