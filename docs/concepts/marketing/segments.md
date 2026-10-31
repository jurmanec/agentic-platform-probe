# Audience segments

**Context:** [E1](../../E1.md) uses segment IDs as the handle an agent resolves before proposing a journey step. For who typically defines vs operates segments at enterprise scale, see [Platform vs marketing ops](platform-vs-marketing-ops.md).

---

## What a segment is

In marketing technology (MarTech), an **audience segment** is a **defined group of customers** you target together — not a single person, and not “everyone.”

Marketers build segments from attributes and behavior, for example:

- **Account / profile:** residential vs business, region (Northeast), active account
- **Behavior:** recently upgraded, opened last email, abandoned cart
- **Consent / compliance:** opted in to email, not on do-not-contact, SMS permitted or not

That group is stored in a platform (often a customer data platform or audience manager) under a stable **segment ID**. Campaigns and journeys reference that ID: *“Run this fiber-upgrade message for `seg_residential_northeast_active`.”*

---

## Why segments matter in workflows

Segments are the bridge between **what you want to say** (campaign brief) and **what you’re allowed to do** (rules, channels, timing):

```text
Campaign brief  →  which segment?  →  segment rules  →  propose journey step  →  validate
     (what)            (who)              (constraints)         (how)              (pass/fail)
```

Downstream systems use the segment to:

1. **Resolve metadata** — name, attributes, channel policy
2. **Load audience rules** — compliance, eligibility, frequency caps
3. **Validate proposals** — e.g. SMS disallowed for this segment

Agentic MarTech work often looks like: given a brief + segment ID, an agent calls tools that encode this lookup and validation chain.

---

## Example (E1 stub)

E1 does **not** implement real segmentation or CDP queries. It uses a fake segment for workflow shape:

| Field | Example value |
|-------|----------------|
| Segment ID | `seg_residential_northeast_active` |
| Meaning | Residential customers, Northeast region, active accounts |
| Channel policy (stub) | Email and in-app allowed; **SMS disallowed** |
| Rule (stub) | `rule_no_sms_residential` — no SMS for residential segments |

The agent passes the segment ID into stub tools (`get_segment`, `get_audience_rules`, `validate_constraints`). See [E1 scenario](../../E1.md#scenario).

---

## What this probe is not claiming

- No real audience builder, SQL, or Adobe Experience Platform integration
- No live customer counts or identity resolution
- Segment definitions are **fixtures in code/JSON**, not production data

The goal is vocabulary and workflow familiarity for the MarTech agentic role probe — not MarTech product depth.

---

## Related terms (future)

- **Journey / journey step** — a timed touchpoint in a multi-step customer experience (E1 proposes one step)
- **Activation** — sending the approved experience to the segment via channels (out of scope for E1)
- **CDP / audience manager** — systems that store segments and traits (stubbed here)
- **Platform vs marketing ops** — [who owns briefs, segments, and platform work](platform-vs-marketing-ops.md)
- **Journey graphs** — [steps as nodes; E1 vs production](journey-graphs.md)
