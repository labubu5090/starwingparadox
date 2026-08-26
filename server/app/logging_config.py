"""Structured logging configuration with JSON/human-readable formats."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

REDACTED_FIELDS = {"password", "token", "secret", "authorization", "cookie", "x-galaxy-api-id"}


def _redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: "***" if k.lower() in REDACTED_FIELDS else _redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(i) for i in obj]
    return obj


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get("-"),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(_redact(log_entry), default=str)


class HumanFormatter(logging.Formatter):
    FORMAT = "%(asctime)s %(levelname)-8s [%(request_id)s] %(name)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        record.request_id = request_id_var.get("-")
        return super().format(record)


def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    for handler in root.handlers[:]:
        root.removeHandler(handler)

    stream = logging.StreamHandler(sys.stdout)
    if json_format:
        stream.setFormatter(JSONFormatter())
    else:
        fmt = HumanFormatter(fmt=HumanFormatter.FORMAT, datefmt=HumanFormatter.DATE_FORMAT)
        stream.setFormatter(fmt)

    root.addHandler(stream)

    for noisy in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
