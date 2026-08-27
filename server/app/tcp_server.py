"""Asyncio TCP server for the Starwing Paradox arcade game protocol.

Handles binary-framed protobuf messages over persistent TCP connections.
Each client gets its own coroutine with incremental buffering, frame decoding,
and handler dispatch.

Usage:
    python -m app.tcp_server
    # or
    from app.tcp_server import main
    asyncio.run(main())
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import subprocess
import sys
from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import settings
from app.logging_config import request_id_var, setup_logging
from app.protocol.codec import (
    HAS_GENERATED,
    decode_length_prefix,
    decode_request,
    encode_length_prefix,
)
from app.protocol.errors import DecodeError, FramingError, UnknownMessageType
from app.protocol.registry import MESSAGE_TYPE_MAP

logger = logging.getLogger(__name__)

HandlerFunc = Callable[
    [int, int, str, bytes],
    Coroutine[Any, Any, bytes | None],
]

_handlers: dict[int, HandlerFunc] = {}
_shutdown_event = asyncio.Event()

MAX_FRAME_SIZE = 1 * 1024 * 1024  # 1 MiB

# ── Connection counter and logging ────────────────────────
_connection_counter: int = 0
_tcp_log_file: Path | None = None


def _get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        result = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            text=True,
            timeout=5,
            stderr=subprocess.DEVNULL,
            cwd=str(Path(__file__).parent.parent.parent),
        )
        return result.strip()
    except Exception:
        return "unknown"


def _setup_tcp_logging() -> Path:
    """Set up timestamped TCP log file and unbuffered output.

    Returns the log file path.
    """
    global _tcp_log_file

    run_id = datetime.now(timezone.utc).strftime("tcp-%Y%m%d-%H%M%S")
    log_dir = Path(__file__).parent.parent.parent / "docs" / "generated" / run_id
    log_dir.mkdir(parents=True, exist_ok=True)
    _tcp_log_file = log_dir / "tcp_server.log"

    # Write startup header
    pid = os.getpid()
    python_exe = sys.executable
    cwd = os.getcwd()
    git_commit = _get_git_commit()
    generated_status = "LOADED" if HAS_GENERATED else "FALLBACK_RAW"

    header = (
        f"=== TCP Server Startup ===\n"
        f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
        f"Git commit: {git_commit}\n"
        f"PID: {pid}\n"
        f"Python: {python_exe}\n"
        f"Working directory: {cwd}\n"
        f"Bind: {settings.app_host}:{settings.pb_port}\n"
        f"Log path: {_tcp_log_file}\n"
        f"Generated-Protobuf: {generated_status}\n"
        f"Raw fallback: {not HAS_GENERATED}\n"
        f"===========================\n"
    )

    with open(_tcp_log_file, "a", encoding="utf-8") as f:
        f.write(header)

    # Also set unbuffered output for this process
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)

    logger.info(
        "TCP server logging: commit=%s pid=%d python=%s cwd=%s bind=%s:%d log=%s protobuf=%s",
        git_commit, pid, python_exe, cwd,
        settings.app_host, settings.pb_port,
        _tcp_log_file, generated_status,
    )

    return _tcp_log_file


def _log_tcp_event(event: str, client_id: str = "", extra: str = "") -> None:
    """Write a timestamped event to the TCP log file and console."""
    global _connection_counter

    ts = datetime.now(timezone.utc).isoformat()
    line = f"[{ts}] {event}"
    if client_id:
        line += f" client={client_id}"
    if extra:
        line += f" {extra}"

    logger.info(line)

    if _tcp_log_file:
        try:
            with open(_tcp_log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass


def register_handler(message_type: int, handler: HandlerFunc) -> None:
    """Register a handler coroutine for a given messageType."""
    _handlers[message_type] = handler
    logger.info(
        "Registered handler: messageType=%d (%s)",
        message_type,
        MESSAGE_TYPE_MAP.get(message_type, "unknown"),
    )


async def handle_message(
    packet_id: int,
    message_type: int,
    message_name: str,
    payload: bytes,
) -> bytes | None:
    """Default handler for unregistered message types.

    Logs the message and returns None (no response).
    """
    logger.warning(
        "No handler registered for messageType=%d (%s), dropping",
        message_type,
        message_name,
    )
    return None


async def _handle_ping(
    packet_id: int,
    message_type: int,
    message_name: str,
    payload: bytes,
) -> bytes | None:
    """Handle Ping (0x66): echo back with the same messageType.

    The legacy protocol (starwing.js:118-123) shows:
      - Client receives Ping (0x66) from server
      - Client replies with PingResponse (0x67) containing unixTimestamp
    So when the game sends Ping (0x66), we echo it back, and the game
    will reply with PingResponse (0x67).
    """
    logger.info("Ping received: packetId=%d", packet_id)
    framed = encode_length_prefix(payload)
    logger.info("Ping reply sent: packetId=%d messageType=0x66", packet_id)
    return framed


register_handler(0x66, _handle_ping)


async def _handle_ping_response(
    packet_id: int,
    message_type: int,
    message_name: str,
    payload: bytes,
) -> bytes | None:
    """Handle PingResponse (0x67 / 103): acknowledge and keep connection alive.

    Source: legacy-js/js/starwing.js:121
      payload = { packetId: decoded.packetId, messageType: 0x67,
                  Ping: { unixTimestamp: parseInt(Date.now()/1000)} };

    The game sends this in response to receiving a Ping (0x66).
    We acknowledge it and keep the connection open for subsequent messages.
    """
    logger.info(
        "PingResponse received: packetId=%d messageType=0x67 (103), "
        "connection alive, waiting for next message",
        packet_id,
    )
    return None


register_handler(0x67, _handle_ping_response)


async def _handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """Process a single client connection."""
    global _connection_counter
    _connection_counter += 1
    conn_num = _connection_counter

    peer = writer.get_extra_info("peername")
    client_id = f"{peer[0]}:{peer[1]}" if peer else "unknown"
    request_id_var.set(client_id)

    _log_tcp_event(
        f"ACCEPT #{conn_num}",
        client_id=client_id,
        extra=f"total_connections={_connection_counter}",
    )

    buffer = bytearray()
    try:
        while not _shutdown_event.is_set():
            try:
                data = await asyncio.wait_for(
                    reader.read(65536),
                    timeout=settings.pb_timeout,
                )
            except TimeoutError:
                _log_tcp_event(f"TIMEOUT #{conn_num}", client_id=client_id)
                break

            if not data:
                _log_tcp_event(f"EOF #{conn_num}", client_id=client_id)
                break

            buffer.extend(data)

            while len(buffer) >= 4:
                try:
                    payload, _ = decode_length_prefix(bytes(buffer))
                except FramingError as exc:
                    if "Incomplete frame" in str(exc):
                        break
                    _log_tcp_event(f"FRAMING_ERROR #{conn_num}", client_id=client_id, extra=str(exc))
                    break

                frame_size = 4 + len(payload)
                buffer = buffer[frame_size:]

                try:
                    packet_id, message_type, message_name, raw_payload = decode_request(
                        encode_length_prefix(bytes(payload))
                    )
                except (FramingError, DecodeError, UnknownMessageType) as exc:
                    _log_tcp_event(f"DECODE_ERROR #{conn_num}", client_id=client_id, extra=str(exc))
                    continue

                request_id_var.set(f"{client_id}:pkt{packet_id}")

                _log_tcp_event(
                    f"RECV #{conn_num}",
                    client_id=client_id,
                    extra=f"packetId={packet_id} messageType={message_type} (0x{message_type:X}) name={message_name}",
                )

                handler = _handlers.get(message_type, handle_message)
                try:
                    response = await handler(packet_id, message_type, message_name, raw_payload)
                except Exception:
                    logger.exception(
                        "Handler error for messageType=%d from %s",
                        message_type,
                        client_id,
                    )
                    continue

                if response is not None:
                    writer.write(response)
                    await writer.drain()
                    _log_tcp_event(
                        f"SEND #{conn_num}",
                        client_id=client_id,
                        extra=f"packetId={packet_id} messageType={message_type} (0x{message_type:X}) bytes={len(response)}",
                    )

    except asyncio.CancelledError:
        _log_tcp_event(f"CANCELLED #{conn_num}", client_id=client_id)
    except (ConnectionResetError, BrokenPipeError, OSError) as exc:
        win_err = getattr(exc, "winerror", None)
        if win_err in (64, 10054):
            _log_tcp_event(
                f"DISCONNECT #{conn_num} (Windows WinError {win_err})",
                client_id=client_id,
            )
        else:
            _log_tcp_event(f"DISCONNECT #{conn_num} (connection reset)", client_id=client_id)
    except Exception:
        logger.exception("Unexpected error for client %s", client_id)
    finally:
        request_id_var.set(client_id)
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()
        _log_tcp_event(f"CLOSED #{conn_num}", client_id=client_id, extra=f"total_connections={_connection_counter}")


async def _run_server(
    host: str = "0.0.0.0",
    port: int = 6666,
) -> None:
    """Start the TCP server and accept connections."""
    _setup_tcp_logging()
    server = await asyncio.start_server(_handle_client, host, port)
    _log_tcp_event(f"LISTEN host={host} port={port}")

    async with server:
        await _shutdown_event.wait()

    _log_tcp_event("SHUTDOWN")
    server.close()
    await server.wait_closed()


async def run_server(
    host: str = "0.0.0.0",
    port: int = 6666,
) -> None:
    """Public entry point: run the server until shutdown is requested."""
    await _run_server(host, port)


async def shutdown_server() -> None:
    """Signal the server to shut down gracefully."""
    logger.info("Shutdown requested")
    _shutdown_event.set()


async def main() -> None:
    """Standalone main: configure logging and run the TCP server."""
    setup_logging(level=settings.log_level)
    logger.info(
        "Starting Starwing Paradox TCP server on %s:%d",
        settings.app_host,
        settings.pb_port,
    )
    try:
        await _run_server(host=settings.app_host, port=settings.pb_port)
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down")
        await shutdown_server()


if __name__ == "__main__":
    asyncio.run(main())
