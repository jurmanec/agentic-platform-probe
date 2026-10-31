"""CLI: python -m e2.run --path happy|fail"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from e2.rag import answer_query  # noqa: E402

HAPPY_QUERY = (
    "Is SMS allowed for residential Northeast active segments?"
)
FAIL_QUERY = (
    "What is the 2099 lunar billboard advertising budget for AcmeCorp?"
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m e2.run",
        description=(
            "E2 thin RAG over a marketing-ops corpus. "
            "Retrieves chunks, answers with citations, or fails closed when unknown."
        ),
    )
    parser.add_argument(
        "--path",
        choices=("happy", "fail"),
        default=None,
        help="happy: in-corpus question. fail: out-of-corpus question (expect unknown).",
    )
    parser.add_argument(
        "--query",
        default=None,
        help="Custom question (overrides --path default query).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="xAI model id (default: grok-3-fast, or env XAI_MODEL).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.query:
        query = args.query
    elif args.path == "fail":
        query = FAIL_QUERY
    else:
        # default happy
        query = HAPPY_QUERY if args.path in (None, "happy") else HAPPY_QUERY

    result = answer_query(query=query, model_name=args.model)
    print(json.dumps(result, indent=2))

    status = result.get("status")
    if args.path == "happy" and status != "answered":
        return 2
    if args.path == "fail" and status != "unknown":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
