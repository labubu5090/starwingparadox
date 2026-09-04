"""Shared raw-hex trace logger for NESYS protocol.

Used by nesys_tcp_stub (TCP 1042) and nesys_pipe (named pipe).
Logs every TX/RX to logs/nesys_trace.log + stdout.
READ-ONLY diagnostic layer — never alters bytes or replies.
"""
from __future__ import annotations

import datetime
import os
import re
import sys
import threading
import time

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_DIR = os.path.join(_SCRIPT_DIR, "..", "logs")
_LOG_PATH = os.path.join(_LOG_DIR, "nesys_trace.log")

_lock = threading.Lock()
_file = None


def _ensure_log() -> None:
    global _file
    if _file is not None:
        return
    try:
        os.makedirs(_LOG_DIR, exist_ok=True)
        _file = open(_LOG_PATH, "a", encoding="utf-8")
    except OSError:
        _file = None


def _hex_dump(data: bytes, width: int = 16) -> str:
    lines: list[str] = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        lines.append(f"    {hex_part:<{width * 3 - 1}}  |{ascii_part}|")
    return "\n".join(lines)


def _card_id_hint(data: bytes) -> str:
    try:
        text = data.decode("ascii", errors="ignore")
        m = re.search(r"card_id[=:]\s*(\d{10,20})", text)
        if m:
            return f"  [hint] possible card id: {m.group(1)}"
        runs = re.findall(r"\b\d{16,20}\b", text)
        if runs:
            return f"  [hint] possible card id: {runs[0]}"
    except Exception:
        pass
    return ""


class TraceLogger:
    def __init__(self, channel: str) -> None:
        self._channel = channel  # "[TCP1042]" or "[PIPE]"
        self._conn_counter = 0
        self._conn_lock = threading.Lock()

    def _next_conn_id(self) -> int:
        with self._conn_lock:
            self._conn_counter += 1
            return self._conn_counter

    def _write(self, line: str) -> None:
        try:
            _ensure_log()
            with _lock:
                if _file is not None:
                    _file.write(line + "\n")
                    _file.flush()
                print(line, flush=True)
        except Exception:
            pass

    def conn_open(self) -> int:
        cid = self._next_conn_id()
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        self._write(f"{ts} {self._channel}[conn#{cid}] client connected")
        return cid

    def conn_close(self, conn_id: int) -> None:
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        self._write(f"{ts} {self._channel}[conn#{conn_id}] client disconnected")

    def rx(self, conn_id: int, data: bytes) -> None:
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        hint = _card_id_hint(data)
        self._write(
            f"{ts} {self._channel}[conn#{conn_id}] RX {len(data)} bytes\n"
            f"{_hex_dump(data)}{hint}"
        )

    def tx(self, conn_id: int, data: bytes) -> None:
        ts = datetime.datetime.now().isoformat(timespec="milliseconds")
        self._write(
            f"{ts} {self._channel}[conn#{conn_id}] TX {len(data)} bytes\n"
            f"{_hex_dump(data)}"
        )
