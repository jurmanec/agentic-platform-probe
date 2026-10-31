"""LangChain + xAI tool-calling loop for the E1 marketing-ops probe.

Uses an explicit bind_tools loop so tool invocations are visible in logs.
"""

from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_xai import ChatXAI

from e1.tools import TOOL_MAP, TOOLS

DEFAULT_MODEL = "grok-3-fast"
MAX_STEPS = 8

SYSTEM_PROMPT = """You are a marketing-ops platform assistant.

Given a campaign brief and a segment ID:
1. Call get_segment to load segment metadata.
2. Call get_audience_rules to load compliance rules.
3. Call propose_journey_step with exactly one journey step (channel, message_theme, timing, rationale).
4. Call validate_constraints on that same proposal.
5. Stop. Do not call more tools after validation.

Rules:
- Use only the tools provided. Do not invent segment data.
- Prefer a channel allowed by the segment's channel_policy.
- After validate_constraints returns, reply with a short confirmation. The CLI will assemble structured JSON from the tool results.
"""

FAIL_PATH_ADDENDUM = """
DEMO FAILURE PATH: You MUST propose channel "sms" in propose_journey_step,
even though the segment disallows SMS. The point is to demonstrate constraint rejection.
"""

def _loads_maybe(text: str) -> Any:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None

def _tool_name(call: Any) -> str:
    if isinstance(call, dict):
        return str(call.get("name") or "")
    return str(getattr(call, "name", "") or "")


def _tool_args(call: Any) -> dict[str, Any]:
    if isinstance(call, dict):
        args = call.get("args") or {}
        return dict(args) if isinstance(args, dict) else {}
    args = getattr(call, "args", {}) or {}
    return dict(args) if isinstance(args, dict) else {}


def _tool_id(call: Any) -> str:
    if isinstance(call, dict):
        return str(call.get("id") or "")
    return str(getattr(call, "id", "") or "")


def assemble_result(segment_id: str, tool_log: list[dict[str, Any]],) -> dict[str, Any]:
    proposal: dict[str, Any] = {}
    validation: dict[str, Any] = {"approved": False, "violations": []}

    for entry in tool_log:
        parsed = _loads_maybe(entry.get("result") or "")
        if not isinstance(parsed, dict):
            continue
        name = entry.get("name")
        if name == "propose_journey_step" and "channel" in parsed:
            proposal = {
                "channel": parsed.get("channel"),
                "message_theme": parsed.get("message_theme"),
                "timing": parsed.get("timing"),
                "rationale": parsed.get("rationale"),
            }
        if name == "validate_constraints":
            validation = {
                "approved": bool(parsed.get("approved")),
                "violations": parsed.get("violations") or [],
            }
            if isinstance(parsed.get("proposal"), dict) and not proposal:
                proposal = parsed["proposal"]

    approved = bool(validation.get("approved"))
    status = "approved" if approved else "rejected"
    if not proposal:
        status = "incomplete"

    return {
        "segment_id": segment_id,
        "proposal": proposal,
        "validation": validation,
        "status": status,
        "tool_calls": [
            {"name": e["name"], "args": e.get("args"), "ok": e.get("ok", True)}
            for e in tool_log
        ],
    }


def run_agent(
    *,
    brief: str,
    segment_id: str,
    path: str = "happy",
    model_name: str | None = None,
) -> dict[str, Any]:
    api_key = os.environ.get("XAI_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "XAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    model_id = model_name or os.environ.get("XAI_MODEL", DEFAULT_MODEL)
    llm = ChatXAI(model=model_id, temperature=0, api_key=api_key).bind_tools(TOOLS)
    system = SYSTEM_PROMPT
    if path == "fail":
        system = SYSTEM_PROMPT + FAIL_PATH_ADDENDUM
    user = (
        f"Campaign brief: {brief}\n"
        f"Segment ID: {segment_id}\n"
        "Look up the segment, propose one journey step, and validate it."
    )
    messages: list[Any] = [SystemMessage(content=system), HumanMessage(content=user)]
    tool_log: list[dict[str, Any]] = []

    for step in range(1, MAX_STEPS + 1):
        ai: AIMessage = llm.invoke(messages)
        messages.append(ai)
        calls = list(getattr(ai, "tool_calls", None) or [])
        if not calls:
            break
        for call in calls:
            name = _tool_name(call)
            args = _tool_args(call)
            call_id = _tool_id(call)
            tool = TOOL_MAP.get(name)
            print(f"[e1] step {step} tool={name} args={json.dumps(args, default=str)}")
            if tool is None:
                result = json.dumps({"error": "unknown_tool", "name": name})
                ok = False
            else:
                result = tool.invoke(args)
                ok = True
                if not isinstance(result, str):
                    result = json.dumps(result)
            tool_log.append({"name": name, "args": args, "result": result, "ok": ok})
            messages.append(
                ToolMessage(content=result, tool_call_id=call_id or name)
            )
    return assemble_result(segment_id, tool_log)
