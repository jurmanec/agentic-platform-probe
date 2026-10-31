# Journey graphs and campaign steps

**Context:** [E1](../../E1.md) proposes **one isolated journey step** for a segment. In production, that step is usually a **node in a larger graph** — or one option chosen at runtime from allowed actions. This page frames the tracer against that business reality.

**See also:** [Audience segments](segments.md), [Platform vs marketing ops](platform-vs-marketing-ops.md), [When LLM inference fits](../llm-inference-fit.md)

---

## Journeys as graphs (typical mental model)

A **customer journey** (or campaign journey) is often modeled as a **directed graph**:

| Graph piece | Marketing meaning |
|-------------|-------------------|
| **Node** | A journey **step** — e.g. send email, wait 3 days, show in-app message, branch on open/click |
| **Edge** | What happens **next** — unconditional follow-up, time delay, or branch condition |
| **Entry** | How audiences enter — segment join, event trigger, API |
| **Exit** | Goal reached, opt-out, timeout, or journey end |

Example (simplified):

```text
[Entry: segment join]
        ↓
   [Email: intro offer]
        ↓
    Wait 3 days
        ↓
   Opened? ──no──→ [Email: reminder]
        │
       yes
        ↓
   [In-app: upgrade CTA]
        ↓
      [Exit]
```

Marketers and ops **author** this structure in journey builders or config systems. Engineering **operates** the platform that stores, validates, schedules, and activates it.

---

## Design time vs run time

| Phase | What happens | Graph involvement |
|-------|----------------|-------------------|
| **Design time** | Build journey template, branches, copy, timing | Full or partial graph defined **before** large-scale send |
| **Activation** | Apply journey to a **segment** (configuration) | Segment-level template |
| **Run time** | Each **customer** moves through nodes; consent, caps, and outcomes apply | Per-customer position in the graph + event history |

E1 collapses all of this into: *given brief + segment, propose one step*. It does **not** model graph position, branches, or per-customer state.

---

## Are full graphs planned upfront?

**Often partially or fully — not always.**

| Pattern | Graph upfront? |
|---------|----------------|
| Regulated multi-touch programs | **Mostly yes** — skeleton + branches planned and reviewed before scale |
| Phased / always-on programs | **Partial** — launch early steps; extend graph as results come in |
| One-shot campaign (single email) | **No graph** — one node only |
| Real-time next-best-action | **Implicit graph** — allowed actions + policies; not always one authored diagram |

Production rarely means “no plan ever,” but it also rarely means “every future step fixed on day one for every program type.”

---

## Where LLMs fit (realistic, high level)

LLMs in agentic marketing platforms are commonly used to **assist** ops workflows, not to autonomously run entire graphs without gates:

- **Draft** a step (channel, theme, timing, copy) from brief + audience context
- **Suggest** next action from **allowed** transitions (not invent any step freely)
- **Lookup** segment metadata, rules, and journey state via **tools**
- **Validate** proposals against policy before human or system approval
- **Activate** only after approval — hand off to platform APIs

If the LLM helps choose **what comes next** in a multi-step journey, it typically needs **graph context**: completed steps, current node, and valid next nodes — not just a campaign brief in isolation.

E1 omits that context on purpose (probe scope).

---

## How E1 maps (and what it omits)

| Production concept | E1 tracer |
|--------------------|-----------|
| Journey graph | **Not modeled** |
| Multiple steps / branches | **One** proposed step only |
| Prior steps / current position | **Not passed** to the model |
| Segment-level step template | **Roughly** — one proposal for the segment ID |
| Per-customer send / consent | **Out of scope** |
| Rule validation before activation | **Stubbed** via `validate_constraints` |
| LLM proposes, platform validates | **Yes** — core pattern the tracer practices |

E1 is useful for: **tool orchestration**, **constraint checking**, and **workflow shape** — not for claiming journey-builder parity.

```text
Production (simplified):  graph + state + rules → propose next → validate → approve → activate

E1 (tracer):              brief + segment → propose one step → validate → JSON out
```

---

## Segment-level vs customer-level (again)

- **Config / ops layer:** “For segment X, step 2 is an email with theme Y” — segment-scoped, common in journey design.
- **Run time:** Platform evaluates each customer (opt-in, frequency, holdouts, branch outcomes).

E1’s segment-level proposal is a **weak but defensible** stand-in for ops/config drafting. It is **not** a model for “one LLM decision broadcasts to millions with no per-customer gates.”

---

## What this doc is not claiming

- No specific journey builder product (Adobe Journey Optimizer, etc.)
- No claim that all enterprises plan graphs the same way
- No claim that LLMs replace marketers or compliance review

**Goal:** When reading E1 results, remember you are exercising **one node’s worth** of a much larger graph-and-governance story — enough to taste platform agent work, not enough to represent full campaign lifecycle management.
