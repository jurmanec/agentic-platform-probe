# Bruno — P5 E3 API collection

Git-native requests for the E3 idempotent RAG API (`POST /ask`).

## Open in Bruno

1. Install [Bruno](https://www.usebruno.com/downloads).
2. **Open Collection** → select this folder: `bruno/p5-e3`.
Environment files use **vars-only** `.bru` syntax (no `meta` block). The environment name comes from the filename (`deployed.bru` → **deployed**).
4. Set `ASK_API_URL` as described in [docs/how-to/bruno-e3.md](../../docs/how-to/bruno-e3.md). Do not put the deployed URL in `environments/deployed.bru`.

## Requests

| Request | Purpose |
|---------|---------|
| `e3/ask-happy.bru` | In-corpus question from [docs/E3.md](../../docs/E3.md) |
| `e3/ask-fail.bru` | Out-of-corpus question from [docs/E3.md](../../docs/E3.md) — expect `status: "unknown"` |

Run the happy-path request twice with unchanged `idempotency_key` to verify cache hit on the second call.

## CLI (optional)

```bash
npx @usebruno/cli run bruno/p5-e3/e3/ask-happy.bru --env deployed
npx @usebruno/cli run bruno/p5-e3/e3/ask-fail.bru --env deployed
```

`ASK_API_URL` must be set in the environment first. See [docs/how-to/bruno-e3.md](../../docs/how-to/bruno-e3.md).
