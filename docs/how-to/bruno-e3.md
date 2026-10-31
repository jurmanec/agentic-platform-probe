# Call the E3 API from Bruno

The collection is [bruno/p5-e3](../../bruno/p5-e3). Requests call `{{baseUrl}}/ask`. `baseUrl` comes from `ASK_API_URL`, not from a URL checked into the repo.

The deployed API has no authorizer. The URL stays in gitignored env files so a public commit does not publish an open endpoint.

## After deploy

Copy `AskApiUrl` from the stack output. No trailing slash.

1. Put it in the repo-root `.env` (see `.env.example`):

   ```bash
   ASK_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com
   ```

2. Copy that same line into `bruno/p5-e3/.env` (see `bruno/p5-e3/.env.example`). The Bruno app loads a `.env` in the collection folder and exposes it as `{{process.env.ASK_API_URL}}`. The committed environment file `environments/deployed.bru` only references that variable.

## Desktop

1. Install [Bruno](https://www.usebruno.com/downloads).
2. Open the collection folder `bruno/p5-e3`.
3. Select the **deployed** environment.
4. Send `e3/ask-happy` twice with the same `idempotency_key`. The second response should be the cached body (`cache.hit` true). `e3/ask-fail` should return `status: "unknown"`.

## CLI

The CLI inherits the shell. Sourcing the repo-root `.env` is enough; you do not need `bruno/p5-e3/.env` for this path.

```bash
set -a
source .env
set +a

npx @usebruno/cli run bruno/p5-e3/e3/ask-happy.bru --env deployed
npx @usebruno/cli run bruno/p5-e3/e3/ask-fail.bru --env deployed
```
