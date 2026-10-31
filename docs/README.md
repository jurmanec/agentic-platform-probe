# P5 documentation

Experiment plans, MarTech concept notes, and slice specs for the agentic platform probe.

**Language:** docs here use **anonymous, GitHub-safe** vocabulary (illustrative enterprise MarTech — no employer, colleague, or req details). Private steering context lives in [P5_CHARTER.md](../P5_CHARTER.md) and `.cursor/internal/`.

| Doc | Purpose |
|-----|---------|
| [E1.md](E1.md) | Tool-using agent slice (**frozen**) |
| [E2.md](E2.md) | Thin RAG slice (**frozen**) |
| [E3.md](E3.md) | Cloud reliability slice — idempotent RAG API (**deployed and tested**) |
| [planning/e3-bedrock.md](planning/e3-bedrock.md) | Bedrock generation behind the E3 Lambda (**proposal**, E3 follow-on) |
| [planning/e4-evals.md](planning/e4-evals.md) | Eval harness over frozen E2 (**proposal**) |
| [how-to/bruno-e3.md](how-to/bruno-e3.md) | Call the deployed E3 API from Bruno without committing the URL |
| [concepts/](concepts/README.md) | Marketing-ops / probe glossary |

Root [README.md](../README.md) has setup and run commands.
