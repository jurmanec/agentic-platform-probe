"""Lambda handler: idempotent POST /ask wrapping e2.rag.answer_query."""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any

import boto3

logger = logging.getLogger()
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

_dynamo_resource = None


def _table():
    global _dynamo_resource
    if _dynamo_resource is None:
        _dynamo_resource = boto3.resource("dynamodb")
    table_name = os.environ.get("IDEMPOTENCY_TABLE", "").strip()
    if not table_name:
        raise RuntimeError("IDEMPOTENCY_TABLE is not configured on the function.")
    return _dynamo_resource.Table(table_name)


def _api_response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _parse_body(event: dict[str, Any]) -> dict[str, Any] | tuple[int, dict[str, Any]]:
    raw = event.get("body") or ""
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    if not raw:
        return 400, {"error": "missing_body", "message": "Request body is required."}
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        return 400, {"error": "invalid_json", "message": "Body must be JSON."}
    if not isinstance(body, dict):
        return 400, {"error": "invalid_json", "message": "Body must be a JSON object."}
    return body


def _validate(body: dict[str, Any]) -> dict[str, str] | tuple[int, dict[str, Any]]:
    query = body.get("query")
    key = body.get("idempotency_key")
    if not query or not str(query).strip():
        return 400, {"error": "validation_error", "message": "query is required."}
    if not key or not str(key).strip():
        return 400, {
            "error": "validation_error",
            "message": "idempotency_key is required.",
        }
    return {"query": str(query).strip(), "idempotency_key": str(key).strip()}


def _from_dynamo(item: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(item["result_json"])
    result["cache"] = {"hit": True}
    return result


def _to_dynamo_item(
    idempotency_key: str, query: str, result: dict[str, Any]
) -> dict[str, str]:
    stored = {k: v for k, v in result.items() if k != "cache"}
    return {
        "idempotency_key": idempotency_key,
        "query": query,
        "result_json": json.dumps(stored),
    }


def handle_ask(*, query: str, idempotency_key: str) -> dict[str, Any]:
    """Core idempotency + RAG logic (testable without API Gateway envelope)."""
    table = _table()
    existing = table.get_item(Key={"idempotency_key": idempotency_key})
    item = existing.get("Item")
    if item:
        logger.info("cache_hit=true idempotency_key=%s", idempotency_key)
        return _from_dynamo(item)

    logger.info(
        "cache_hit=false idempotency_key=%s invoking_llm=true", idempotency_key
    )

    if not os.environ.get("XAI_API_KEY", "").strip():
        raise RuntimeError("XAI_API_KEY is not configured on the function.")

    from e2.rag import answer_query

    result = answer_query(query=query)
    result["cache"] = {"hit": False}
    table.put_item(Item=_to_dynamo_item(idempotency_key, query, result))
    return result


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    parsed = _parse_body(event)
    if isinstance(parsed, tuple):
        code, err = parsed
        return _api_response(code, err)

    validated = _validate(parsed)
    if isinstance(validated, tuple):
        code, err = validated
        return _api_response(code, err)

    try:
        result = handle_ask(
            query=validated["query"],
            idempotency_key=validated["idempotency_key"],
        )
        return _api_response(200, result)
    except RuntimeError as exc:
        logger.exception("configuration_error")
        return _api_response(
            500, {"error": "configuration_error", "message": str(exc)}
        )
    except Exception:
        logger.exception(
            "internal_error idempotency_key=%s", validated["idempotency_key"]
        )
        return _api_response(
            500, {"error": "internal_error", "message": "Request failed."}
        )
