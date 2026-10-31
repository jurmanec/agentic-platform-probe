```sh
set -a
source .env
set +a

sam build
sam deploy --parameter-overrides "XaiApiKey=${XAI_API_KEY}"
```

