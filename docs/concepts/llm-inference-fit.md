# When LLM inference fits a business problem

**Context:** [E1](../../E1.md) uses an LLM to draft a journey step and orchestrate stub tools. This page asks: *when is that a sensible production pattern,* and *where does the tracer honestly meet or miss that bar?*

**See also:** [Journey graphs](marketing/journey-graphs.md), [Platform vs marketing ops](marketing/platform-vs-marketing-ops.md), [LangChain message types](langchain/message-types.md)

---

## A practical decision frame

Use LLM inference when the problem has **most** of these properties:

| Criterion | Meaning |
|-----------|---------|
| **Unstructured or variable input** | Natural-language briefs, notes, tickets — not a fixed form with ten enum fields |
| **Judgment or synthesis** | Combine multiple sources into one decision or draft |
| **Language output matters** | Themes, copy, explanations — not just a boolean or ID lookup |
| **Human or workflow review before action** | Draft → validate → approve; model is not the last gate |
| **Tool-backed facts** | Grounding via APIs, DB, rules — model must not invent segment data or policy |
| **Cost of errors is manageable** | Wrong draft caught by validation; not silent production sends |

Avoid LLM as the **primary** mechanism when:

| Anti-pattern | Prefer instead |
|--------------|----------------|
| Deterministic lookup | API / database query |
| Hard compliance rules | Rules engine, policy code, allowlists |
| Exact graph traversal | Journey engine, scheduler, state machine |
| High-stakes autonomous action | Human approval + idempotent activation APIs |
| Problem solvable with a template | Config, templates, or simple heuristics |

**Rule of thumb:** LLM for **drafting and explaining**; traditional code for **facts, gates, and execution**.

---

## Split the workflow: who should do what?

In agentic marketing-ops shapes (and in E1), roles divide cleanly:

```text
Facts (tools)     →  get_segment, get_audience_rules, get_journey_context (future)
Draft (LLM)       →  propose step, theme, timing, rationale
Gate (code)       →  validate_constraints, consent checks, rate limits
Execute (platform)→  activation APIs (out of scope for E1)
```

| Step | LLM appropriate? | Why |
|------|------------------|-----|
| Load segment metadata | **No** | Structured data; lookup |
| Load audience rules | **No** | Structured data; lookup |
| Map brief → message theme | **Often yes** | Language understanding |
| Choose channel among *allowed* options | **Sometimes** | Could be rules; LLM adds synthesis with brief |
| Suggest timing | **Mixed** | Heuristics or ML; LLM acceptable as draft |
| Write **rationale** for reviewers | **Often yes** | Explanation for humans / audit trail |
| Approve / reject vs policy | **No** | Must be deterministic and testable |
| Activate to customers | **No** | Platform job; not inference |

The **`rationale`** field in E1’s `propose_journey_step` is the clearest business case for inference: *why this step given brief + segment context?* That supports ops copilot and approval workflows even when channel choice could be templated.

---

## Production patterns that justify LLM (high level)

Realistic uses in enterprise marketing technology (illustrative):

1. **Ops copilot** — Marketer supplies a brief; agent drafts a governed platform action with explanation.
2. **Brief → structured config** — Translate messy intent into fields the journey/CDP API accepts.
3. **Multi-source synthesis** — Brief + segment traits + journey position + notes → one proposed next step.
4. **Assistive copy / theme** — Draft message angles; separate review before send.

Less realistic as *LLM-only* solutions:

- Replacing the journey engine or decisioning core  
- Autonomous segment-wide sends without validation  
- Storing authoritative segment or consent data inside the model  

---

## How E1 meets the criteria

| Criterion | E1 |
|-----------|-----|
| Unstructured input | **Partially** — default brief is short but natural language; `--brief` can vary |
| Judgment / synthesis | **Partially** — model picks theme, timing, channel after tool lookups |
| Language output | **Yes** — `message_theme`, `rationale` |
| Review before action | **Implied** — `validate_constraints` + JSON out; no auto-activation (correct for probe) |
| Tool-backed facts | **Yes** — segment/rules from fixtures; prompt forbids inventing data |
| Errors manageable | **Yes** — fail path demos rejection; no customer impact |

**What E1 practices well (aligned with production direction):**

- **Tool orchestration** — model decides call order within prompt bounds  
- **Deterministic validation** after LLM draft  
- **Structured handoff** — `propose_journey_step` records fields validation can check  
- **Separation of intent vs facts** — `AIMessage` tool calls vs `ToolMessage` results ([message types](langchain/message-types.md))

**Primary probe value:** learning **agentic platform glue**, not proving every field requires a frontier model.

---

## How E1 does *not* meet the criteria (honest limits)

| Gap | Why it matters |
|-----|----------------|
| **Single step, no journey graph** | Production “next step” needs graph state — see [journey graphs](marketing/journey-graphs.md) |
| **`propose_journey_step` is a passthrough** | Python only JSON-packages LLM args; no persistence, templates, or copy API |
| **Channel choice is weak LLM territory** | With one segment stub, “pick email” could be a rule |
| **Fixed tool sequence in system prompt** | Reduces orchestration novelty; production agents need richer planning |
| **One segment fixture** | Little variety in synthesis problem |
| **No human-in-the-loop UI** | Output is CLI JSON, not an approval queue |
| **Pedagogical over necessity** | Same happy path could be scripted for demo purposes |

**Verdict:** E1 **demonstrates the shape** of a defensible LLM use case (draft + explain + validate) but **overuses inference** for parts that production would often hard-code (lookup order, trivial channel pick). That is acceptable for an 8–12h tracer if you do not overclaim in conversation or portfolio copy.

---

## Scorecard: E1 vs “would we ship this LLM?”

| E1 component | Ship LLM in production? | E1 role |
|--------------|---------------------------|---------|
| `get_segment` / `get_audience_rules` | **No** — APIs | Stub tools ✓ |
| Orchestration (which tools when) | **Maybe** — simple flows can be code | LLM + prompt ✓ (learning) |
| `message_theme` from brief | **Often yes** | LLM ✓ |
| `rationale` | **Often yes** | LLM ✓ |
| `channel` selection | **Sometimes** — rules first | LLM (weak necessity) |
| `validate_constraints` | **No** — rules engine | Code ✓ |
| Activation | **No** | Omitted ✓ |

---

## Questions to ask before adding LLM to a real feature

Use these when evaluating a MarTech or platform feature (including extensions after E1):

1. Can a **deterministic function** do this with equal reliability?  
2. Where does **ground truth** live — and does the model **call tools** to reach it?  
3. What happens when the model is wrong — is there a **hard gate** before side effects?  
4. Does a human or workflow need an **explanation** (`rationale`)?  
5. Is the input **language-heavy** (briefs, tickets) or **already structured** (IDs, enums)?  
6. Are we optimizing for **learning agent patterns** (probe) or **minimum production complexity**?

If (1) is yes and (4)–(5) are no, skip LLM for that slice.

---

## What this doc is not claiming

- No vendor or employer-specific deployment patterns  
- No claim that E1’s LLM usage is minimal or optimal — only that it is **explainable**  
- Not a substitute for security, cost, or eval design for production agents  

**Goal:** Read E1 as a **deliberate sample** of “draft with LLM, validate with code, don’t activate blindly” — and know exactly which parts are tracer shortcuts versus patterns worth carrying into real platform work.
