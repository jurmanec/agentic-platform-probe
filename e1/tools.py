"""In-process stub tools standing in for an audience / policy platform."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from langchain_core.tools import tool

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@lru_cache(maxsize=1)
def _segments() -> dict:
    return json.loads((FIXTURES / "segments.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _rules() -> dict:
    return json.loads((FIXTURES / "rules.json").read_text(encoding="utf-8"))


def _dumps(payload: object) -> str:
    return json.dumps(payload, indent=2)


@tool
def get_segment(segment_id: str) -> str:
    """Return metadata for an audience segment (name, channel policy, attributes)."""
    segment = _segments().get(segment_id)
    if segment is None:
        return _dumps({"error": "unknown_segment", "segment_id": segment_id})
    return _dumps(segment)


@tool
def get_audience_rules(segment_id: str) -> str:
    """Return compliance / eligibility rules for a segment."""
    bundle = _rules().get(segment_id)
    if bundle is None:
        return _dumps({"error": "unknown_segment", "segment_id": segment_id, "rules": []})
    return _dumps(bundle)

@tool
def propose_journey_step(
    brief: str,
    segment_id: str,
    channel: str,
    message_theme: str,
    timing: str,
    rationale: str,
) -> str:
    """Record one proposed journey step (channel, theme, timing) for the brief + segment.

    Call this after looking up the segment and its rules. Prefer an allowed channel.
    """
    proposal = {
        "brief": brief,
        "segment_id": segment_id,
        "channel": channel.strip().lower(),
        "message_theme": message_theme,
        "timing": timing,
        "rationale": rationale,
    }
    return _dumps(proposal)


@tool
def validate_constraints(
    segment_id: str,
    channel: str,
    message_theme: str,
    timing: str,
) -> str:
    """Check a journey-step proposal against the segment's audience rules."""
    channel_norm = channel.strip().lower()
    violations = []
    bundle = _rules().get(segment_id, {"rules": []})
    for rule in bundle.get("rules", []):
        forbidden = (rule.get("constraint") or {}).get("channel_not")
        if forbidden and channel_norm == str(forbidden).lower():
            violations.append(
                {
                    "rule_id": rule.get("rule_id"),
                    "reason": rule.get("description")
                    or f"Channel '{channel_norm}' is not allowed for this segment.",
                }
            )
    segment = _segments().get(segment_id)
    if segment:
        policy = (segment.get("channel_policy") or {}).get(channel_norm)
        if policy == "disallowed" and not violations:
            violations.append(
                {
                    "rule_id": "rule_channel_policy",
                    "reason": f"Channel '{channel_norm}' is disallowed by segment channel policy.",
                }
            )
    return _dumps(
        {
            "segment_id": segment_id,
            "proposal": {
                "channel": channel_norm,
                "message_theme": message_theme,
                "timing": timing,
            },
            "approved": len(violations) == 0,
            "violations": violations,
        }
    )


TOOLS = [
    get_segment,
    get_audience_rules,
    propose_journey_step,
    validate_constraints,
]

TOOL_MAP = {t.name: t for t in TOOLS}
