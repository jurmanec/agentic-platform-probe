# E4 — Eval harness over frozen E2 (proposal)

**Status:** Proposal (not started)  
**Parent:** [P5_CHARTER.md](../../P5_CHARTER.md)  
**Depends on:** [E2.md](../E2.md) (frozen), [E3.md](../E3.md) (active until frozen)

---

## Goal

Score the frozen E2 cite / refuse contract with a small golden set. E2’s CLI (`python -m e2.run --path happy|fail`) only checks `status`. An eval runner is the same idea with more cases and graders that fail the run when retrieval or the answer contract slips.

This slice answers: *Can I tell a retrieval or grounding regression from a lucky smoke test?*

E1 and E2 stay frozen. The harness calls them as the system under test. A failing case is a finding. Changing `MIN_SCORE`, the prompt, or retrieval is an explicit E2 reopen, not an eval fix.

Freeze [E3](../E3.md) before treating this as the active slice. The retrieval layer does not need AWS, so it can be sketched beside E3.

---

## What to measure

E2 already has the contract worth grading: lexical retrieve, a score gate (`MIN_SCORE = 2` in `e2/rag.py`), then cite or refuse.

Two layers. Most of the demo does not spend API calls.

### Retrieval (no LLM)

Call `e2.rag.retrieve` only. This is the regression suite and the layer to re-run while editing cases.

| Case | Expect |
|------|--------|
| SMS / residential Northeast question | Top hit is `channel-policy.md`, score ≥ 2 |
| Paraphrase (“Can we text residential customers in the Northeast?”) | Same doc |
| Frequency question (“promotional email per calendar day”) | `channel-policy.md` still in the top hits |
| Lunar billboard budget | No hit at or above 2 |
| Near miss (“residential advertising budget”) | Below the gate, or a hit that is not treated as an answer — this case is why `MIN_SCORE` exists |

### Generation (one xAI call per case, small N)

Call `e2.rag.answer_query` and grade the JSON it already returns.

- In-corpus: `status == "answered"`, at least one citation whose `path` is a real file under `e2/corpus/`, and the answer mentions the policy fact (SMS disallowed / `rule_no_sms_residential`).
- Out-of-corpus: `status == "unknown"`, `citations == []`.

Do not grade prose with another model in v1. The fail-closed signal is already structured. Add an LLM-as-judge later only for a check code cannot make, such as “the answer contradicts the cited excerpt.” Three short markdown files do not need a second model to decide whether the first one followed its prompt.

---

## Shape

Same CLI spirit as `python -m e2.run`:

```text
e4/
  cases.jsonl     # golden queries + expectations
  graders.py      # pure checks over retrieve() / answer_query() results
  run.py          # python -m e4.run --layer retrieval|generation
```

Print one JSON object per case plus a pass/fail summary. Exit `2` if anything fails, matching `e2/run.py`.

Cases are JSONL, not an eval framework. A case is a query plus a few assertions:

```json
{"id":"sms-residential","layer":"generation","query":"Is SMS allowed for residential Northeast active segments?","expect":{"status":"answered","citation_path":"channel-policy.md","answer_contains":["SMS","not allowed"]}}
{"id":"lunar-budget","layer":"generation","query":"What is the 2099 lunar billboard advertising budget for AcmeCorp?","expect":{"status":"unknown","citations_empty":true}}
```

Retrieval cases use `min_top_score` and `must_include_path` instead of `status`.

---

## Relationship to E3

Run evals against `answer_query`, not `POST /ask`. The DynamoDB idempotency cache would replay the first answer for a repeated key and hide a real regression. E3 stays the reliability slice; E4 stays the quality slice.

---

## Out of scope (this proposal)

- Reopening E1 or E2 (prompt, threshold, chunking, embeddings)
- RAGAS, DeepEval, LangSmith, or a hosted eval product
- LLM-as-judge in v1
- Scoring the deployed Lambda or idempotency cache
- E1 tool-loop evals (happy-path channel in `{email, in-app}`, fail-path constraint rejection) — a later stretch; the agent loop is flakier and more expensive than E2’s structured JSON

---

## Suggested order

1. Retrieval cases and graders. No API key. This is the demo if time runs out.
2. A handful of generation cases reusing the E2 happy and fail queries plus one paraphrase and one near miss.
3. Record failures as findings. Do not “fix” them inside `e2/rag.py` unless E2 is explicitly reopened.

---

## How to use this with the next LLM

1. This file is a **proposal**. Do not implement E4 unless asked.
2. **E1 and E2 stay frozen.** E3 stays the active slice until it is frozen.
3. Stay anonymous in `docs/`, README, and code.
4. Prefer the retrieval layer over an eval framework or a judge model.
