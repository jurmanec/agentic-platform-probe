# Platform engineering vs marketing operations

**Context:** Why [E1](../../E1.md) gives the agent **platform tools** (segment lookup, rules, validation) rather than asking it to invent audiences from raw customer data.

**See also:** [Audience segments](segments.md)

---

## Typical division of labor (enterprise scale)

At a large enterprise, marketing technology is **shared work**. No single team “owns everything.” The split below is illustrative — real org charts vary.

| Lane | Owns (typical) | Does not usually own |
|------|----------------|----------------------|
| **Marketing / business** | Campaign briefs, audience *intent*, segment *selection* and definition in self-service tools, journey/creative strategy, activation decisions | Data pipelines, identity resolution, platform uptime, low-level integrations |
| **Engineering (platform)** | Ingestion pipelines, customer profile stores, audience/CDP APIs, activation plumbing, governance hooks, **agentic automation built on top of platforms** | Day-to-day campaign copy, choosing which segment to target for a launch |
| **Data / analytics** (often middle) | Complex segment logic, data quality, metric definitions; sometimes SQL-side audiences when UI tools are insufficient | Campaign strategy; running the full platform stack |

Marketing works **through** platforms engineering builds. Engineering does not replace marketing judgment — it makes governed data and workflows available at scale.

---

## End-to-end flow (simplified)

```text
Sources (billing, product, web, consent, CRM)
        ↓
Engineering: ingest → unify identity → store profiles & traits
        ↓
Platform: segments, rules, channel policies (APIs / audience tools)
        ↓
Marketing: campaign brief + pick/create segment in business terms
        ↓
Platform + agents: lookup segment, validate proposal, activate journey step
```

**Campaign brief** = what marketing wants to achieve.  
**Segment ID** = which audience bucket (already defined or created in platform tools).  
**Stub tools in E1** = stand-ins for that platform lookup layer — not a replacement for marketing’s brief or segment strategy.

---

## Where agentic platform engineering fits

Roles focused on **agentic marketing platforms** usually sit on the **engineering** side:

- Integrate LLMs with existing data and marketing systems
- Expose **tools** (segment metadata, rules, validation) agents can call safely
- Automate multi-step operational workflows (draft → check → hand off)
- Own reliability, APIs, and standards — not creative direction

The E1 agent is a **workflow helper over platform capabilities**, similar in spirit to how your P0/P1 work orchestrated systems others defined — here the “upstream” actor is marketing ops, the “platform” is audience and rules data.

---

## How this maps to E1

| Real world (conceptual) | E1 stub |
|-------------------------|---------|
| Marketing writes brief | Fixed campaign brief in CLI fixture |
| Marketing selects segment | `segment_id` passed in |
| Platform resolves segment | `get_segment` |
| Platform / policy store | `get_audience_rules` |
| Ops or agent drafts journey step | `propose_journey_step` (LLM-assisted) |
| Platform enforces constraints | `validate_constraints` |

E1 does **not** build a CDP, train marketers, or ingest live customer data. It practices **tool orchestration** in a marketing-shaped workflow.

---

## What this doc is not claiming

- No specific employer org chart, team names, or vendor stack
- No claim that boundaries are always clean — handoffs and overlap are normal
- Not interview prep for marketing roles — this clarifies **platform engineering** scope for the probe

The goal is reference clarity: **marketing defines and uses audiences; engineering builds and operates the systems (and agents) that make that safe and scalable.**
