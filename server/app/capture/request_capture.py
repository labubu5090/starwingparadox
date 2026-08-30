"""Request contract capture for unresolved HTTP 501 routes.

Captures request metadata only:
- timestamp, method, path, content_type, body_length
- body SHA-256 hash (never raw body)
- root format, JSON key names and value types
- form field names if form-encoded
- selected local profile UUID (server-side)
- response status

Does NOT log raw bodies, credentials, card data, or identity values.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from fastapi import Request

logger = logging.getLogger(__name__)
_capture_logger = logging.getLogger("app.capture")


def _compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _detect_format(content_type: str) -> str:
    if "json" in content_type:
        return "json"
    if "form" in content_type:
        return "form-urlencoded"
    if "xml" in content_type:
        return "xml"
    if "text" in content_type:
        return "text"
    return "binary"


def _extract_json_metadata(data: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"parse_error": True}

    if isinstance(obj, dict):
        return {
            "root_type": "object",
            "keys": {
                k: type(v).__name__ for k, v in obj.items()
            },
        }
    if isinstance(obj, list):
        return {
            "root_type": "array",
            "length": len(obj),
            "element_type": type(obj[0]).__name__ if obj else "empty",
        }
    return {"root_type": type(obj).__name__}


def _extract_form_metadata(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return {"parse_error": True}

    pairs = text.split("&")
    fields = {}
    for pair in pairs:
        if "=" in pair:
            key = pair.split("=", 1)[0]
            fields[key] = "str"
    return {"root_type": "form", "fields": fields}


async def capture_request_metadata(
    request: Request,
    endpoint: str,
    response_status: int,
    selected_profile_uuid: str | None = None,
) -> None:
    """Capture request metadata for contract discovery.

    Args:
        request: FastAPI request object
        endpoint: Human-readable endpoint name
        response_status: Response HTTP status code
        selected_profile_uuid: Server-side selected profile UUID if any
    """
    content_type = request.headers.get("content-type", "")
    body = await request.body()
    body_length = len(body)
    body_sha256 = _compute_sha256(body) if body else "empty"

    format_type = _detect_format(content_type)
    body_metadata: dict[str, Any] = {}

    if body:
        if format_type == "json":
            body_metadata = _extract_json_metadata(body)
        elif format_type == "form-urlencoded":
            body_metadata = _extract_form_metadata(body)
        else:
            body_metadata = {"root_type": format_type}

    _capture_logger.info(
        "CAPTURE %s %s status=%d body_len=%d sha256=%s format=%s keys=%s profile=%s",
        request.method,
        request.url.path,
        response_status,
        body_length,
        body_sha256[:16],
        format_type,
        list(body_metadata.get("keys", {}).keys()) if "keys" in body_metadata else [],
        selected_profile_uuid or "none",
    )

    return None  # noqa: RET501 – side-effect only
