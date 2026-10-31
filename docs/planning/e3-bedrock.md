# E3 follow-on — Amazon Bedrock generation (proposal)

**Status:** Proposal (not started)  
**Parent:** [E3.md](../E3.md)  
**Depends on:** E3 frozen on the current xAI path first  
**Related:** [E2.md](../E2.md) (frozen), [planning/e4-evals.md](e4-evals.md) (separate proposal)

---

## Goal

Demonstrate Amazon Bedrock as the generation client behind the E3 Lambda. The cite / refuse JSON stays the one E2 already returns. Retrieval stays lexical.

This is a follow-on to E3, not a new experiment. E1, E2, and E3 each ask a different question (tools, grounded retrieval, reliability). Bedrock asks E3’s question again: the model call is AWS glue, and the credential is the function’s IAM role instead of `XAI_API_KEY`. The eval harness in [e4-evals.md](e4-evals.md) would be a new experiment because it measures quality. This document does not start that work.

Freeze [E3](../E3.md) on xAI first. Its done definition is the idempotent API (happy, fail, one LLM call on retry). Bedrock comes after that, the same kind of optional later depth as the E3.1 note in [E3.md](../E3.md). E3.1 stays the async E1 idea. This follow-on is generation-provider depth only.

---

## What the demo shows

`e2.rag.answer_query` builds `ChatXAI` itself and requires `XAI_API_KEY`. `e3/handler.py` imports that function. `template.yaml` passes `XaiApiKey` into the function environment. A Bedrock demo cannot be only an environment change.

The change is a small seam at the generation call:

- Default remains `ChatXAI`, so the frozen E2 CLI and the frozen E3 xAI deploy keep their current behavior.
- When the Lambda selects Bedrock, generation uses the Converse API. LangChain `ChatBedrockConverse` matches the `SystemMessage` / `HumanMessage` pattern already in `e2/rag.py`.
- The function role gains `bedrock:InvokeModel` in the same region as the Lambda. Drop `XAI_API_KEY` on that path.
- One on-demand model. Model access must be enabled in that region before deploy.
- `retrieve`, `MIN_SCORE`, the corpus, and the `answered` / `unknown` JSON stay as they are.

The no-evidence branch in `answer_query` returns `status: "unknown"` before any model call. The lunar-budget query still proves that gate: Bedrock is not invoked. The SMS / residential query proves Converse runs and citations still attach.

Re-run E3’s three paths against the Bedrock function: happy (`cache.hit` false), fail (`status: "unknown"`), idempotent retry (cached body, one model call total). Compare `status` and citation shape with the frozen xAI run. Same contract, different provider.

---

## Shape

```text
e2/rag.py           # seam only: optional chat model; default ChatXAI
e3/handler.py       # select Bedrock from env when configured
template.yaml       # bedrock:InvokeModel on the function role; model id env
```

Suggested environment on the Bedrock path:

| Variable | Role |
|----------|------|
| `BEDROCK_MODEL_ID` | On-demand model id in the function’s region. Presence selects Bedrock. |
| `IDEMPOTENCY_TABLE` | Unchanged. |

No new package, corpus, or endpoint. `POST /ask` and the idempotency key stay the E3 contract.

A local run with AWS credentials is optional parity. The demonstration is the deployed function, because the point is the execution role.

---

## Relationship to the eval proposal

[e4-evals.md](e4-evals.md) grades `answer_query` output and does not call `POST /ask`. Those graders still apply if this follow-on lands first: generation cases become a provider comparison. This proposal does not require the eval harness. The E2 happy and fail queries are enough to freeze the follow-on.

Run any comparison against `answer_query` or against a fresh idempotency key. A repeated key returns the cached first provider and hides a real difference.

---

## Out of scope (this proposal)

- Knowledge Bases (would replace the markdown corpus and the keyword scorer)
- Bedrock Agents (would replace the frozen E1 tool loop)
- Guardrails as the refusal mechanism (the retrieval gate already refuses when nothing clears `MIN_SCORE`)
- Embeddings, Titan or otherwise (deferred E2 path)
- Hosted Bedrock model-evaluation jobs
- Changing `MIN_SCORE`, chunking, or the grounded prompt
- Replacing the frozen xAI E2 CLI default
- A new experiment id, a new repo, or a second API

---

## Suggested order

1. Freeze E3 on xAI: happy, fail, and idempotent retry on the deployed API.
2. Add the generation seam. Default stays `ChatXAI`. Confirm `python -m e2.run --path happy` and `--path fail` still pass.
3. Enable one on-demand model in the Lambda region. Grant `bedrock:InvokeModel`. Set `BEDROCK_MODEL_ID`. Remove `XAI_API_KEY` from that function.
4. Re-run happy, fail, and idempotent retry. Record that `status` and citation shape match the xAI run, and that the fail path does not call the model.

---

## How to use this with the next LLM

1. This file is a **proposal**. Do not implement it unless asked.
2. **Freeze E3 on xAI first.** Do not swap providers mid-slice.
3. **E1 stays frozen.** Touch `e2/rag.py` only for the generation seam. Leave retrieval and the default xAI CLI path in place.
4. Stay anonymous in `docs/`, README, and code.
5. Prefer one Converse model behind the existing Lambda over Knowledge Bases, Agents, or Guardrails.
