"""Invoke the Lambda handler locally with a synthetic API Gateway event.

Requires IDEMPOTENCY_TABLE (deployed stack table or local DynamoDB) and XAI_API_KEY.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from e2.run import FAIL_QUERY, HAPPY_QUERY  # noqa: E402
from e3.handler import lambda_handler  # noqa: E402


def _event(body: dict) -> dict:
    return {
        "version": "2.0",
        "routeKey": "POST /ask",
        "rawPath": "/ask",
        "body": json.dumps(body),
        "isBase64Encoded": False,
        "requestContext": {"http": {"method": "POST", "path": "/ask"}},
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m e3.local_run",
        description="Local E3 handler smoke (needs DynamoDB table + XAI_API_KEY).",
    )
    parser.add_argument(
        "--path",
        choices=("happy", "fail", "retry"),
        default="happy",
        help="happy/fail: first request. retry: repeat happy with same idempotency key.",
    )
    parser.add_argument("--idempotency-key", default=None, help="Override idempotency key.")
    parser.add_argument("--query", default=None, help="Override query text.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if not os.environ.get("IDEMPOTENCY_TABLE", "").strip():
        print(
            "IDEMPOTENCY_TABLE is not set. Deploy the SAM stack first or export the table name.",
            file=sys.stderr,
        )
        return 1

    args = parse_args(argv)
    if args.path == "fail":
        query = args.query or FAIL_QUERY
        key = args.idempotency_key or f"local-fail-{uuid.uuid4().hex[:8]}"
    elif args.path == "retry":
        query = args.query or HAPPY_QUERY
        key = args.idempotency_key or "local-retry-demo"
    else:
        query = args.query or HAPPY_QUERY
        key = args.idempotency_key or f"local-happy-{uuid.uuid4().hex[:8]}"

    resp = lambda_handler(_event({"query": query, "idempotency_key": key}), None)
    print(json.dumps(resp, indent=2))
    body = json.loads(resp["body"])

    if args.path == "happy" and body.get("status") != "answered":
        return 2
    if args.path == "fail" and body.get("status") != "unknown":
        return 2
    if args.path == "retry" and body.get("cache", {}).get("hit") is not True:
        print(
            "Expected cache.hit=true on retry. Run --path happy --idempotency-key local-retry-demo first.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
