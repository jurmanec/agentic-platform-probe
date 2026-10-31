"""CLI: python -m e1.run --path happy|fail"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from e1.agent import run_agent  # noqa: E402

DEFAULT_BRIEF = (
    "Promote a new fiber upgrade to existing residential customers in the Northeast."
)
DEFAULT_SEGMENT = "seg_residential_northeast_active"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m e1.run",
        description=(
            "E1 tool-using marketing-ops agent. "
            "Looks up a stub segment, proposes one journey step, validates constraints."
        )
    )
    parser.add_argument(
        "--path",
        choices=("happy", "fail"),
        default="happy",
        help="happy: agent should pick an allowed channel. fail: force SMS to demo rejection.",
    )
    parser.add_argument("--brief", default=DEFAULT_BRIEF, help="Campaign brief text.")
    parser.add_argument(
        "--segment-id",
        default=DEFAULT_SEGMENT,
        help="Stub segment ID (see e1/fixtures/segments.json).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="xAI model id (default: grok-3-fast, or env XAI_MODEL).",
    )
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv) 
    result = run_agent(
        brief=args.brief,
        segment_id=args.segment_id,
        path=args.path,
        model_name=args.model,
    )
    print(json.dumps(result, indent=2))
    if result.get("status") == "incomplete":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
