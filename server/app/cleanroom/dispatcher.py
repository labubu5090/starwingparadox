"""Dispatch foundation for clean-room protocol foundation.

This module implements a minimal request-dispatch abstraction with
explicit handler registration, direction validation, eligibility
checking, and lifecycle constraints.
"""
from __future__ import annotations

import logging
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

from app.cleanroom.commands import CommandCatalog, CommandInfo, Direction, ImplementationStatus
from app.cleanroom.errors import (
    DuplicateHandlerError,
    UnsupportedCommandError,
    WrongDirectionError,
)
from app.cleanroom.events import EventLog, EventType

if TYPE_CHECKING:
    from app.cleanroom.state import SessionStateMachine

logger = logging.getLogger(__name__)

HandlerFunc = Callable[[Any, int, str, bytes], Coroutine[Any, Any, bytes | None]]


class Dispatcher:
    """Minimal request-dispatch abstraction.

    Requirements:
    - handlers registered explicitly
    - no dynamic module import from command input
    - no eval, no exec
    - duplicate handler registration rejected
    - unsupported command rejected
    - handler direction validated
    - handler eligibility checked
    - lifecycle constraints checked before dispatch
    - deterministic synthetic response behavior
    - no real card, account, payment or identity operation
    """

    def __init__(
        self,
        catalog: CommandCatalog,
        state_machine: SessionStateMachine,
        event_log: EventLog | None = None,
    ) -> None:
        self._catalog = catalog
        self._state_machine = state_machine
        self._event_log = event_log
        self._handlers: dict[int, tuple[HandlerFunc, CommandInfo]] = {}

    def register(
        self,
        message_type: int,
        handler: HandlerFunc,
    ) -> None:
        """Register a handler for a message type.

        Args:
            message_type: Numeric message type identifier.
            handler: Async handler function.

        Raises:
            DuplicateHandlerError: If handler already registered.
            UnsupportedCommandError: If command not in catalog or not eligible.
            WrongDirectionError: If handler direction is wrong.
        """
        cmd = self._catalog.get_by_id(message_type)
        if cmd is None:
            raise UnsupportedCommandError(
                f"No catalog entry for message type 0x{message_type:02x}"
            )

        if cmd.implementation != ImplementationStatus.ELIGIBLE:
            raise UnsupportedCommandError(
                f"Command {cmd.symbolic_name} is not eligible for implementation "
                f"(status: {cmd.implementation.value})"
            )

        if cmd.direction != Direction.CLIENT_TO_SERVICE:
            raise WrongDirectionError(
                f"Cannot register service-to-client command "
                f"{cmd.symbolic_name} as handler"
            )

        if message_type in self._handlers:
            raise DuplicateHandlerError(
                f"Handler already registered for message type "
                f"0x{message_type:02x}"
            )

        self._handlers[message_type] = (handler, cmd)

    def unregister(self, message_type: int) -> None:
        """Unregister a handler for a message type.

        Args:
            message_type: Numeric message type identifier.
        """
        self._handlers.pop(message_type, None)

    async def dispatch(
        self,
        message_type: int,
        packet_id: int,
        message_name: str,
        payload: bytes,
    ) -> bytes | None:
        """Dispatch a command to its registered handler.

        Args:
            message_type: Numeric message type.
            packet_id: Packet identifier.
            message_name: Symbolic message name.
            payload: Raw payload bytes.

        Returns:
            Response bytes or None.

        Raises:
            UnsupportedCommandError: If no handler registered.
            WrongDirectionError: If wrong direction.
        """
        # Validate lifecycle state
        self._state_machine.validate_command_allowed()

        # Look up handler
        if message_type not in self._handlers:
            if self._event_log:
                self._event_log.record(
                    EventType.UNSUPPORTED_COMMAND,
                    source="dispatcher",
                    details={"message_type": message_type},
                )
            raise UnsupportedCommandError(
                f"No handler for message type 0x{message_type:02x}"
            )

        handler, cmd = self._handlers[message_type]

        # Validate direction
        if cmd.direction != Direction.CLIENT_TO_SERVICE:
            raise WrongDirectionError(
                f"Cannot dispatch service-to-client command "
                f"{cmd.symbolic_name}"
            )

        try:
            result = await handler(packet_id, message_type, message_name, payload)
            if self._event_log and result is not None:
                self._event_log.record(
                    EventType.FRAME_SENT,
                    source="dispatcher",
                    details={"message_type": message_type},
                )
            return result
        except Exception:
            logger.exception(
                "Handler error for message type 0x%02x", message_type
            )
            raise

    def is_registered(self, message_type: int) -> bool:
        """Check if a handler is registered for the message type.

        Args:
            message_type: Numeric message type.

        Returns:
            True if handler is registered.
        """
        return message_type in self._handlers

    def get_handler(
        self, message_type: int
    ) -> tuple[HandlerFunc, CommandInfo] | None:
        """Get the handler and command info for a message type.

        Args:
            message_type: Numeric message type.

        Returns:
            Tuple of (handler, CommandInfo) or None.
        """
        return self._handlers.get(message_type)

    def registered_types(self) -> list[int]:
        """Return all registered message types.

        Returns:
            List of registered message types.
        """
        return list(self._handlers.keys())
