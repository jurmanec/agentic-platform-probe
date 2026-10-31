# Idempotency key

**Context:** [E3](../../E3.md) exposes the frozen E2 RAG pipeline behind an HTTP API. Clients send an `idempotency_key` with each `POST /ask` request. DynamoDB stores the first result under that key; retries return the cached response without a second LLM call.

**See also:** [E2](../../E2.md) (what gets wrapped), [LLM inference fit](../llm-inference-fit.md) (when LLM calls belong in production workflows)

---

## What it is

An **idempotency key** is a client-supplied string that identifies **one logical operation**, independent of how many times the HTTP request is actually sent.

Example request body:

```json
{
  "query": "Is SMS allowed for residential Northeast active segments?",
  "idempotency_key": "demo-happy-001"
}
```

The server uses the key as a lookup: *“Have I already processed this operation?”*

- **First time** — run the work (here: `answer_query`), store the result, return it.
- **Same key again** — return the stored result; do **not** repeat the expensive or non-deterministic step.

---

## Why it exists

Networked systems retry. A client may send the same request twice because of:

- Timeouts (no response received → retry)
- Gateway or load-balancer retries
- Application-level retry on 5xx
- Accidental double-submit (UI, script, test harness)

Without idempotency, each retry is a **new** operation. For LLM-backed APIs that causes real problems:

| Retry without idempotency | Effect |
|---------------------------|--------|
| Duplicate LLM calls | Extra latency and cost |
| Different model output | Same “question” yields different answers |
| Duplicate side effects | In APIs that write or activate, retries can double-apply |

An idempotency key lets the client say: *“These two HTTP attempts are the same intended ask — treat them as one.”*

That is standard **platform** discipline for costly, slow, or side-effecting operations. E3 uses it to show production glue around LLM calls, not just CLI invocation.

---

## How E3 uses it

```text
POST /ask { query, idempotency_key }
       │
       ▼
  DynamoDB get(idempotency_key)
       │
       ├─ found → return cached JSON (cache hit; no LLM call)
       │
       └─ not found → answer_query(query)
                      → DynamoDB put(idempotency_key, result)
                      → return JSON
```

**First request** with `"demo-happy-001"`: Lambda calls xAI via E2, persists the full response (including `status: "answered"` or `status: "unknown"`), returns it with `cache.hit: false`.

**Second identical request** (same key and query): Lambda reads DynamoDB, returns the same JSON with `cache.hit: true`. CloudWatch should show no second LLM invocation.

---

## Client responsibilities

1. **Generate a new key for each new logical question.** Reusing a key means “this is a retry of the same operation,” not “cache this query for reuse.”
2. **Keep key + body stable across retries.** If the client retries, it must send the same `idempotency_key` and the same `query`. Changing the query but reusing the key is a client bug.
3. **Keys should be unique enough to avoid collisions.** Common choices: UUID, or a deterministic id derived from `(tenant, operation, client_request_id)` in larger systems. E3 demos use simple strings like `demo-happy-001`.

---

## What gets cached

In E3, the **entire E2 result** is stored: answer, citations, `status`, retrieval metadata.

That includes **fail-closed** outcomes. If the first call returns `status: "unknown"` (out-of-corpus question), a retry with the same key returns the same unknown — still idempotent, still no second LLM call.

---

## Idempotency vs other patterns

| Pattern | Purpose |
|---------|---------|
| **Idempotency key** | Same logical operation, safe retries → same outcome |
| **General cache** | Speed up repeated reads; often keyed only by query, TTL-based |
| **Request deduplication** | Server-side window (e.g. hash of body in last N seconds) |
| **Correlation ID** | Trace/logging across services; does not imply safe retry |

E3 intentionally uses **idempotency** (explicit client key + durable store), not an implicit query cache. That matches how many enterprise APIs document retry behavior.

---

## Out of scope in E3 v1

- Auth binding (which client owns which key)
- Key expiration / TTL in DynamoDB
- Conflict detection if the same key is sent with a **different** query body (v1 may assume well-behaved clients; production APIs often return `409 Conflict`)

Those are reasonable E3.1 or production hardening topics; the tracer focuses on the core retry-safe contract.
