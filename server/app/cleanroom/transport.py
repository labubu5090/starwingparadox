"""Abstract transport interface for clean-room protocol foundation.

This module defines a generic byte transport contract that does not
know about Windows named pipes, certificates, Registry, NESYS
production hosts, card data, cabinet identity, or game-specific
command semantics.
"""
from __future__ import annotations

import abc


class Transport(abc.ABC):
    """Abstract asynchronous transport for byte-level communication.

    Implementations must not:
    - reference Windows named-pipe paths
    - reference certificates or private keys
    - reference Registry values
    - reference NESYS production hosts
    - reference card data or cabinet identity
    - reference game-specific command semantics
    """

    @abc.abstractmethod
    async def open(self) -> None:
        """Open the transport connection.

        Raises:
            TransportStateError: If transport is already open.
        """

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the transport connection.

        After closing, send and receive must raise TransportClosedError.
        """

    @abc.abstractmethod
    async def send(self, data: bytes) -> None:
        """Send bytes through the transport.

        Args:
            data: Bytes to send.

        Raises:
            TransportClosedError: If transport is not open.
            TransportStateError: If transport is in invalid state.
        """

    @abc.abstractmethod
    async def receive(self) -> bytes:
        """Receive bytes from the transport.

        Returns:
            Received bytes.

        Raises:
            TransportClosedError: If transport is not open.
            TransportTimeoutError: If receive times out.
            TransportStateError: If transport is in invalid state.
        """

    @abc.abstractmethod
    def is_open(self) -> bool:
        """Return whether the transport is currently open."""

    @abc.abstractmethod
    async def wait_for_disconnect(self) -> None:
        """Wait for the transport to be disconnected by the remote end.

        Raises:
            TransportTimeoutError: If disconnect does not occur within timeout.
        """
