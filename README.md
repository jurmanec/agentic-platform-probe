# P5 — Agentic platform probe

Illustrative **marketing-ops** experiments: a tool-using agent (E1), later thin RAG (E2) and a cloud reliability slice (E3). Domain vocabulary is fake; this is not a production marketing platform.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set XAI_API_KEY
```

Python 3.11+ recommended.

## E1 — tool-using agent (frozen)

Happy path (allowed channel):

```bash
python -m e1.run --path happy
```

Failure path (SMS proposed, constraint rejected):

```bash
python -m e1.run --path fail
```

See [docs/E1.md](docs/E1.md). Concepts: [when LLM inference fits](docs/concepts/llm-inference-fit.md), [audience segments](docs/concepts/marketing/segments.md), [journey graphs](docs/concepts/marketing/journey-graphs.md), [platform vs marketing ops](docs/concepts/marketing/platform-vs-marketing-ops.md), [LangChain message types](docs/concepts/langchain/message-types.md).

## E2 — thin RAG (frozen)

Happy path (in-corpus question):

```bash
python -m e2.run --path happy
```

Fail path (out-of-corpus → unknown):

```bash
python -m e2.run --path fail
```

Plan: [docs/E2.md](docs/E2.md). Retrieval is lexical (keyword overlap); generation uses xAI.

## E3 — idempotent RAG API (deployed and tested)

Wraps frozen E2 behind API Gateway + Lambda + DynamoDB idempotency. Plan: [docs/E3.md](docs/E3.md). Concept: [idempotency key](docs/concepts/e3/idempotency-key.md).

### Deploy (AWS SAM)

Prerequisites: [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html), AWS credentials, `XAI_API_KEY`. Local Python must match the Lambda runtime in `template.yaml` (currently **3.13** — same as this project's `.venv`).

```bash
source .venv/bin/activate
pip install -r requirements.txt

# First deploy (guided — saves settings to samconfig.toml, gitignored)
sam build
sam deploy --guided
# When prompted for XaiApiKey, use the same value as XAI_API_KEY in .env

# Later deploys
sam build && sam deploy
```

Note the stack outputs `AskApiUrl` and `IdempotencyTableName`.

**Bruno:** Open collection [bruno/p5-e3](bruno/p5-e3) in [Bruno](https://www.usebruno.com/). Set `ASK_API_URL` as described in [docs/how-to/bruno-e3.md](docs/how-to/bruno-e3.md).

### Smoke tests (curl)

Replace `$API` with `AskApiUrl` from deploy output (no trailing slash).

Happy path (first request — `cache.hit` false):

```bash
curl -s -X POST "$API/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"Is SMS allowed for residential Northeast active segments?","idempotency_key":"demo-happy-001"}'
```

Fail path (out-of-corpus — `status` unknown):

```bash
curl -s -X POST "$API/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the 2099 lunar billboard advertising budget for AcmeCorp?","idempotency_key":"demo-fail-001"}'
```

Idempotent retry (repeat happy body — `cache.hit` true, no second LLM call):

```bash
curl -s -X POST "$API/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"Is SMS allowed for residential Northeast active segments?","idempotency_key":"demo-happy-001"}'
```

Check CloudWatch logs for `cache_hit=true` on the retry.

### Local handler smoke (optional)

Uses the **deployed** DynamoDB table name:

```bash
export IDEMPOTENCY_TABLE=<IdempotencyTableName from stack output>
python -m e3.local_run --path happy
python -m e3.local_run --path fail
python -m e3.local_run --path happy --idempotency-key local-retry-demo
python -m e3.local_run --path retry --idempotency-key local-retry-demo
```
