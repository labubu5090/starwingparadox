"""Live request capture middleware for contract discovery.

Logs every incoming request to tutorial/game_data/player routes
with full metadata. Writes structured JSON lines to a capture log file.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.capture.live")

_CAPTURE_DIR = Path(os.environ.get(
    "STARWING_LIVE_CAPTURE_DIR",
    str(Path(__file__).resolve().parents[3] / "artifacts" / "phase_2a_g40"),
))
_CAPTURE_LOG: Path | None = None
_ENABLED = True


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _detect_format(ct: str) -> str:
    if "json" in ct:
        return "json"
    if "form" in ct:
        return "form-urlencoded"
    if "xml" in ct:
        return "xml"
    if "text" in ct:
        return "text"
    return "binary"


def _extract_json_keys(data: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"parse_error": True}
    if isinstance(obj, dict):
        return {
            "root_type": "object",
            "keys": {k: type(v).__name__ for k, v in obj.items()},
        }
    if isinstance(obj, list):
        return {
            "root_type": "array",
            "length": len(obj),
            "element_type": type(obj[0]).__name__ if obj else "empty",
        }
    return {"root_type": type(obj).__name__}


def _extract_form_fields(data: bytes) -> dict[str, Any]:
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


def _write_capture(entry: dict[str, Any]) -> None:
    global _CAPTURE_LOG
    if _CAPTURE_LOG is None:
        _CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        _CAPTURE_LOG = _CAPTURE_DIR / "live_capture.jsonl"
    with open(_CAPTURE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


class LiveCaptureMiddleware(BaseHTTPMiddleware):
    """Logs all requests to tutorial/game_data/player with full metadata."""

    CAPTURE_PREFIXES = ("/tutorial/", "/game_data/", "/player/", "/matching/")

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        should_capture = any(path.startswith(p) for p in self.CAPTURE_PREFIXES)

        if not should_capture:
            return await call_next(request)

        start = time.monotonic()
        content_type = request.headers.get("content-type", "")
        x_galaxy_api_id = request.headers.get("x-galaxy-api-id", "")
        method = request.method

        body = await request.body()
        body_length = len(body)
        body_sha256 = _sha256(body) if body else "empty"
        format_type = _detect_format(content_type)

        body_meta: dict[str, Any] = {}
        if body:
            if format_type == "json":
                body_meta = _extract_json_keys(body)
            elif format_type == "form-urlencoded":
                body_meta = _extract_form_fields(body)
            else:
                body_meta = {"root_type": format_type}

        response = await call_next(request)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)

        resp_ct = response.headers.get("content-type", "")

        entry = {
            "timestamp": time.time(),
            "method": method,
            "path": path,
            "content_type": content_type,
            "body_length": body_length,
            "body_sha256": body_sha256 if body else None,
            "format": format_type,
            "body_keys": body_meta.get("keys"),
            "body_root_type": body_meta.get("root_type"),
            "form_fields": body_meta.get("fields"),
            "x_galaxy_api_id": x_galaxy_api_id or None,
            "response_status": response.status_code,
            "response_content_type": resp_ct,
            "elapsed_ms": elapsed_ms,
        }

        _write_capture(entry)

        logger.info(
            "LIVE_CAPTURE %s %s status=%d body_len=%d sha256=%s format=%s keys=%s elapsed=%sms",
            method,
            path,
            response.status_code,
            body_length,
            body_sha256[:16] if body else "-",
            format_type,
            list(body_meta.get("keys", {}).keys()) if "keys" in body_meta else [],
            elapsed_ms,
        )

        return response
