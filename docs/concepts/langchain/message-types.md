# SystemMessage, HumanMessage, AIMessage, ToolMessage

**Context:** [E1](../../E1.md) uses LangChain message types to run a simple **tool-calling loop** (model → tool calls → tool results → model continues).

This page is a **concept reference** (anonymous, public-safe). It is not vendor-specific.

---

## What each message type represents

### `SystemMessage`
An **instruction** to steer the model’s behavior for the whole run.

Typical contents:
- “You are a platform assistant…”
- “Call tools in this order…”
- “Stop after validation…”

In E1, the system prompt lives in `e1/agent.py` as `SYSTEM_PROMPT`.

### `HumanMessage`
The **user input** for the run.

Typical contents:
- “Here is a campaign brief…”
- “Use this segment ID…”

In E1, the CLI supplies `brief` and `segment_id`, then the code wraps them in a `HumanMessage`.

### `AIMessage`
The **model’s response**.

In a tool-calling setup, an `AIMessage` may contain:
- Normal text (final answer), or
- **Tool call requests**, exposed via `ai.tool_calls`

In E1, this is the object returned by `llm.invoke(messages)` and appended to `messages`.

### `ToolMessage`
The **result of executing a tool call**.

When the model requests a tool call, your code:
1. Extracts the tool name + arguments from the `AIMessage`
2. Executes the tool implementation (or stub)
3. Appends a `ToolMessage` containing the tool result

The next model call sees both the original messages and the tool results, so it can:
- decide whether to call more tools, and/or
- produce the final structured output.

---

## How the tool-calling loop works (conceptual)

```text
SystemMessage (rules/instructions)
HumanMessage  (brief + segment id)
        ↓
LLM → AIMessage
        ↓ (if AIMessage includes tool_calls)
Run tools → ToolMessage(s)
        ↓
LLM again → new AIMessage
        ↓
Stop when there are no more tool calls
```

In E1, the loop continues until the `AIMessage` includes no `tool_calls` or until the max step count is reached.

---

## Why both `AIMessage` and `ToolMessage` are needed

They separate two concerns:

- `AIMessage` = the model’s **intent** (“call `get_segment` with these args”)
- `ToolMessage` = the system’s **facts** (“`get_segment` returned this data”)

That separation is what makes the conversation grounded: the model can reason over real tool outputs instead of guessing.

---

## Where to look in this repo

- Tool-calling loop + message construction: `e1/agent.py`
- Stub tools: `e1/tools.py`
- Fixtures: `e1/fixtures/*.json`

