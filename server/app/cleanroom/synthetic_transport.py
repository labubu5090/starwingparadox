"""Synthetic in-memory transport for unit and integration tests.

This transport is explicitly synthetic and must never default to a
production path or external endpoint. It contains no production
hostnames, no certificate material, and no credentials.
"""
from __future__ import annotations

import asyncio

from app.cleanroom.errors import (
    TransportClosedError,
    TransportStateError,
    TransportTimeoutError,
)
from app.cleanroom.transport import Transport


class SyntheticTransport(Transport):
    """In-memory transport for deterministic testing.

    This transport supports:
    - deterministic queued inbound frames
    - captured outbound frames
    - explicit open and close
    - configurable synthetic disconnect
    - configurable synthetic timeout
    - optional maximum frame size
    - inspection of sent data by tests
    - no threads, no filesystem side effects, no sockets
    """

    def __init__(
        self,
        *,
        max_frame_size: int = 1024 * 1024,
        timeout: float = 30.0,
    ) -> None:
        self._max_frame_size = max_frame_size
        self._timeout = timeout
        self._is_open = False
        self._inbound: asyncio.Queue[bytes | None] = asyncio.Queue()
        self._outbound: list[bytes] = []
        self._disconnect_event = asyncio.Event()

    async def open(self) -> None:
        if self._is_open:
            raise TransportStateError("Transport already open")
        self._is_open = True
        self._disconnect_event.clear()

    async def close(self) -> None:
        self._is_open = False
        self._disconnect_event.set()
        self._inbound.put_nowait(None)

    async def send(self, data: bytes) -> None:
        if not self._is_open:
            raise TransportClosedError("Transport is closed")
        self._outbound.append(data)

    async def receive(self) -> bytes:
        if not self._is_open:
            raise TransportClosedError("Transport is closed")
        try:
            result = await asyncio.wait_for(
                self._inbound.get(), timeout=self._timeout
            )
        except asyncio.TimeoutError as exc:
            raise TransportTimeoutError("Receive timed out") from exc
        if result is None:
            self._is_open = False
            raise TransportClosedError("Transport disconnected")
        if len(result) > self._max_frame_size:
            raise TransportStateError("Frame exceeds maximum size")
        return result

    def is_open(self) -> bool:
        return self._is_open

    async def wait_for_disconnect(self) -> None:
        await self._disconnect_event.wait()

    def inject(self, data: bytes) -> None:
        """Inject data into the inbound queue for the receiver.

        Args:
            data: Bytes to inject.
        """
        self._inbound.put_nowait(data)

    def inject_disconnect(self) -> None:
        """Inject a synthetic disconnect signal."""
        self._inbound.put_nowait(None)

    def get_sent(self) -> list[bytes]:
        """Return all data sent through this transport.

        Returns:
            List of sent byte payloads.
        """
        return list(self._outbound)

    def clear_sent(self) -> None:
        """Clear the outbound capture buffer."""
        self._outbound.clear()

    def sent_count(self) -> int:
        """Return the number of frames sent.

        Returns:
            Number of sent frames.
        """
        return len(self._outbound)
