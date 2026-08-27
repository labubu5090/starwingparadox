"""Raw request/response capture for cabinet network debugging.

Disabled by default. Enable via STARWING_CAPTURE_ENABLED=1.

Captures are written to a directory outside tracked source
(configurable via STARWING_CAPTURE_DIR, default: ../cabinet-captures).
Each capture produces a .meta.json sidecar alongside raw bytes.

Phase 2A adds structured capture sessions with provenance tracking.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
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

PROVENANCE_REAL_CABINET = "REAL_CABINET_CAPTURE"
PROVENANCE_SYNTHETIC = "SYNTHETIC_CAPTURE_TEST"
PROVENANCE_REPLAY = "CABINET_CAPTURE_REPLAY"
PROVENANCE_LEGACY = "LEGACY_SOURCE_DERIVED"


# ---------------------------------------------------------------------------
# Legacy capture API (preserved for backward compatibility)
# ---------------------------------------------------------------------------


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
    global _ENABLED, _CAPTURE_DIR
    _ENABLED = False
    _CAPTURE_DIR = None
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


# ---------------------------------------------------------------------------
# Phase 2A structured capture
# ---------------------------------------------------------------------------


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def redact_identifier(value: str, visible_chars: int = 4) -> str:
    if len(value) <= visible_chars * 2:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars * 2) + value[-visible_chars:]


@dataclass
class CaptureConfig:
    enabled: bool = False
    raw_enabled: bool = False
    redact_identifiers: bool = True
    capture_dir: str = "./data/captures"
    max_body_size: int = 1024 * 1024

    @classmethod
    def from_env(cls) -> CaptureConfig:
        return cls(
            enabled=os.environ.get("CAPTURE_ENABLED", "false").lower() in ("true", "1"),
            raw_enabled=os.environ.get("CAPTURE_RAW_ENABLED", "false").lower() in ("true", "1"),
            redact_identifiers=os.environ.get("CAPTURE_REDACT_IDENTIFIERS", "true").lower()
            in ("true", "1"),
            capture_dir=os.environ.get("CAPTURE_DIR", "./data/captures"),
        )


@dataclass
class HTTPCapture:
    capture_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: str = ""
    client_address: str = ""
    method: str = ""
    path: str = ""
    query_string: str = ""
    request_headers: dict[str, str] = field(default_factory=dict)
    request_content_type: str = ""
    request_byte_length: int = 0
    request_sha256: str = ""
    raw_request_filename: str = ""
    response_status: int = 0
    response_content_type: str = ""
    response_headers: dict[str, str] = field(default_factory=dict)
    response_byte_length: int = 0
    response_sha256: str = ""
    raw_response_filename: str = ""
    handler_classification: str = ""
    database_effect: str = "NO_DATABASE_EFFECT"
    decode_result: str = ""
    error_result: str = ""
    provenance: str = PROVENANCE_REAL_CABINET


@dataclass
class TCPCapture:
    capture_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    connection_id: str = ""
    remote_address: str = ""
    connection_open_ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    frame_sequence: int = 0
    prefix_bytes: str = ""
    declared_length: int = 0
    received_length: int = 0
    payload_sha256: str = ""
    raw_payload_filename: str = ""
    decode_result: str = ""
    message_type: int = 0
    oneof_selection: str = ""
    has_session_id: bool = False
    response_prefix: str = ""
    response_payload_sha256: str = ""
    raw_response_filename: str = ""
    connection_close_ts: str = ""
    error: str = ""
    provenance: str = PROVENANCE_REAL_CABINET


class CaptureSession:
    def __init__(self, session_name: str, config: CaptureConfig | None = None):
        self.session_name = session_name
        self.session_id = str(uuid.uuid4())
        self.config = config or CaptureConfig.from_env()
        self.started_at = datetime.now(timezone.utc)
        self.stopped_at: str | None = None
        self.http_captures: list[HTTPCapture] = []
        self.tcp_captures: list[TCPCapture] = []
        self._session_dir: Path | None = None

    def start(self) -> Path:
        if not self.config.enabled:
            raise RuntimeError("Capture is disabled. Set CAPTURE_ENABLED=true to activate.")
        timestamp = self.started_at.strftime("%Y%m%d_%H%M%S")
        self._session_dir = Path(self.config.capture_dir) / f"{self.session_name}_{timestamp}"
        self._session_dir.mkdir(parents=True, exist_ok=True)
        (self._session_dir / "http").mkdir(exist_ok=True)
        (self._session_dir / "tcp").mkdir(exist_ok=True)
        (self._session_dir / "raw").mkdir(exist_ok=True)
        metadata = {
            "session_name": self.session_name,
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "provenance": PROVENANCE_REAL_CABINET,
        }
        (self._session_dir / "session_metadata.json").write_text(json.dumps(metadata, indent=2))
        return self._session_dir

    def record_http(self, capture: HTTPCapture) -> None:
        capture.session_id = self.session_id
        self.http_captures.append(capture)

    def record_tcp(self, capture: TCPCapture) -> None:
        capture.session_id = self.session_id
        self.tcp_captures.append(capture)

    def stop(self) -> dict[str, Any]:
        self.stopped_at = datetime.now(timezone.utc).isoformat()
        return {
            "session_name": self.session_name,
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "stopped_at": self.stopped_at,
            "http_captures": len(self.http_captures),
            "tcp_captures": len(self.tcp_captures),
        }
