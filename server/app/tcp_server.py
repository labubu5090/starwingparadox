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
from collections.abc import Callable, Coroutine
from typing import Any

from app.config import settings
from app.logging_config import request_id_var, setup_logging
from app.protocol.codec import (
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

    Returns framed raw payload since we don't require generated protobuf for Ping.
    """
    logger.info("Ping received: packetId=%d", packet_id)
    framed = encode_length_prefix(payload)
    logger.info("Ping reply sent: packetId=%d", packet_id)
    return framed


register_handler(0x66, _handle_ping)


async def _handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """Process a single client connection."""
    peer = writer.get_extra_info("peername")
    client_id = f"{peer[0]}:{peer[1]}" if peer else "unknown"
    request_id_var.set(client_id)

    logger.info("Client connected: %s", client_id)

    buffer = bytearray()
    try:
        while not _shutdown_event.is_set():
            try:
                data = await asyncio.wait_for(
                    reader.read(65536),
                    timeout=settings.pb_timeout,
                )
            except TimeoutError:
                logger.info("Connection timed out: %s", client_id)
                break

            if not data:
                logger.info("Client disconnected (EOF): %s", client_id)
                break

            buffer.extend(data)

            while len(buffer) >= 4:
                try:
                    payload, _ = decode_length_prefix(bytes(buffer))
                except FramingError as exc:
                    if "Incomplete frame" in str(exc):
                        break
                    logger.warning("Framing error from %s: %s", client_id, exc)
                    break

                frame_size = 4 + len(payload)
                buffer = buffer[frame_size:]

                try:
                    packet_id, message_type, message_name, raw_payload = decode_request(
                        encode_length_prefix(bytes(payload))
                    )
                except (FramingError, DecodeError, UnknownMessageType) as exc:
                    logger.warning("Decode error from %s: %s", client_id, exc)
                    continue

                request_id_var.set(f"{client_id}:pkt{packet_id}")

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
                    logger.debug("Response sent to %s: %d bytes", client_id, len(response))

    except asyncio.CancelledError:
        logger.info("Client handler cancelled: %s", client_id)
    except Exception:
        logger.exception("Unexpected error for client %s", client_id)
    finally:
        request_id_var.set(client_id)
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()
        logger.info("Client disconnected: %s", client_id)


async def _run_server(
    host: str = "0.0.0.0",
    port: int = 6666,
) -> None:
    """Start the TCP server and accept connections."""
    server = await asyncio.start_server(_handle_client, host, port)
    logger.info("TCP server listening on %s:%d", host, port)

    async with server:
        await _shutdown_event.wait()

    logger.info("TCP server shutting down")
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
