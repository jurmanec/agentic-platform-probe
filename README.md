# Agentic platform probe

A short, freezeable look at agentic platform work in an illustrative marketing-ops setting. The domain data is synthetic. This is not a production marketing platform.

A marketer can describe a campaign in a sentence. The systems around that sentence want a structured step, a cited policy answer, or a repeatable API call. The probe asks where a model helps with that handoff, and where ordinary code should stay in charge.

## Slices

| Slice | Question | What shipped |
| --- | --- | --- |
| **E1** — tool-using agent | Can a model turn a campaign brief and a known segment into one legal journey step? | Frozen. The agent loads the segment and the channel rules, drafts channel, theme, timing, and a rationale, and code rejects a step that breaks policy. Nothing is sent. |
| **E2** — thin RAG | Can an answer stay inside a small policy corpus? | Frozen. Lexical retrieval, then a grounded answer with citations. If the corpus does not support the question, the result is `unknown`. |
| **E3** — idempotent ask API | Can that grounded answer be called twice without calling the model twice? | Deployed and tested. API Gateway, Lambda, and DynamoDB. The caller supplies an idempotency key; a retry returns the stored JSON. |

E1 and E2 are local. E3 wraps the frozen E2 answer path.

## What this leaves out

One segment fixture and four stub tools. Keyword overlap instead of embeddings. No authorizer on the ask API. No message send, no journey graph, and no claim of a production agent platform.

Two follow-ons are written down and not started: [Amazon Bedrock as the generation client](docs/planning/e3-bedrock.md), and an [eval harness over frozen E2](docs/planning/e4-evals.md).

## Read next

- [E1](docs/E1.md), [E2](docs/E2.md), [E3](docs/E3.md) — slice specs and how to run them
- [Case notes](docs/case-study/e1/case_study_notes.md) — the brief-to-step story behind E1
- [Idempotency key](docs/concepts/e3/idempotency-key.md) — where the E3 key comes from
- [Setup, run, and deploy](docs/how-to/setup-run-deploy.md), [deploy E3](docs/how-to/deploy-e3.md), and [call it from Bruno](docs/how-to/bruno-e3.md)
- [Documentation index](docs/README.md)
