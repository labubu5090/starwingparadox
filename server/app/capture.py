"""Raw request/response capture for cabinet network debugging.

Disabled by default. Enable via STARWING_CAPTURE_ENABLED=1.

Captures are written to a directory outside tracked source
(configurable via STARWING_CAPTURE_DIR, default: ../cabinet-captures).
Each capture produces a .meta.json sidecar alongside raw bytes.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CAPTURE_DIR: Path | None = None
_ENABLED: bool = False

SECRET_PATTERN = re.compile(
    r"(password|token|secret|authorization|cookie|x-galaxy-api-id)",
    re.IGNORECASE,
)
REDACTED = "***"
CABINET_ID_REDACTION = re.compile(r"\b\d{10,}\b")


def is_capture_enabled() -> bool:
    return _ENABLED


def get_capture_dir() -> Path | None:
    return _CAPTURE_DIR


def enable_capture(capture_dir: Path | None = None) -> Path:
    global _ENABLED, _CAPTURE_DIR
    _ENABLED = True
    if capture_dir is None:
        default = os.environ.get(
            "STARWING_CAPTURE_DIR",
            str(Path(__file__).resolve().parents[1] / "cabinet-captures"),
        )
        capture_dir = Path(default)
    capture_dir.mkdir(parents=True, exist_ok=True)
    _CAPTURE_DIR = capture_dir
    logger.warning("Capture ENABLED -> %s", _CAPTURE_DIR)
    return _CAPTURE_DIR


def disable_capture() -> None:
    global _ENABLED
    _ENABLED = False
    logger.warning("Capture DISABLED")


def redact_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k: REDACTED if SECRET_PATTERN.search(k) else v for k, v in headers.items()}


def redact_cabinet_id(text: str) -> str:
    return CABINET_ID_REDACTION.sub(REDACTED, text)


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique_filename(prefix: str, ext: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    short_id = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{short_id}.{ext}"


def capture_request_response(
    *,
    correlation_id: str,
    endpoint: str,
    client_ip: str,
    cabinet_id: str | None,
    request_headers: dict[str, str],
    request_body: bytes,
    response_body: bytes,
    response_status: int,
    protobuf_message_type: str | None = None,
    include_raw_request: bool = False,
    include_raw_response: bool = False,
) -> Path | None:
    if not _ENABLED or _CAPTURE_DIR is None:
        return None

    meta: dict[str, Any] = {
        "capture_ts": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "endpoint": endpoint,
        "client_ip": client_ip,
        "cabinet_id_redacted": redact_cabinet_id(cabinet_id) if cabinet_id else None,
        "request_headers": redact_headers(request_headers),
        "request_body_length": len(request_body),
        "request_body_sha256": _hash_bytes(request_body),
        "response_status": response_status,
        "response_body_length": len(response_body),
        "response_body_sha256": _hash_bytes(response_body),
        "protobuf_message_type": protobuf_message_type,
    }

    if include_raw_request:
        meta["raw_request_length"] = len(request_body)
    if include_raw_response:
        meta["raw_response_length"] = len(response_body)

    entry_dir = _CAPTURE_DIR
    meta_name = _unique_filename("capture", "meta.json")
    meta_path = entry_dir / meta_name
    meta_path.write_text(json.dumps(meta, indent=2, default=str), encoding="utf-8")

    if include_raw_request and request_body:
        req_name = meta_name.replace(".meta.json", ".req.bin")
        (entry_dir / req_name).write_bytes(request_body)

    if include_raw_response and response_body:
        resp_name = meta_name.replace(".meta.json", ".resp.bin")
        (entry_dir / resp_name).write_bytes(response_body)

    logger.info("Capture written: %s", meta_path)
    return meta_path


def _init_from_settings() -> None:
    global _ENABLED, _CAPTURE_DIR
    env_val = os.environ.get("STARWING_CAPTURE_ENABLED", "0")
    _ENABLED = env_val in ("1", "true", "yes")
    if _ENABLED:
        dir_env = os.environ.get(
            "STARWING_CAPTURE_DIR",
            str(Path(__file__).resolve().parents[1] / "cabinet-captures"),
        )
        _CAPTURE_DIR = Path(dir_env)
        _CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        logger.warning("Capture pre-enabled from env -> %s", _CAPTURE_DIR)


_init_from_settings()
