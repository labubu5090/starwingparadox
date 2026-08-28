"""Synthetic lifecycle controller for clean-room protocol foundation.

This module orchestrates the abstract transport, synthetic transport,
command decoder/catalog, state machine, and dispatcher into a
runnable lifecycle controller.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.cleanroom.commands import CommandCatalog
from app.cleanroom.dispatcher import Dispatcher, HandlerFunc
from app.cleanroom.errors import (
    CleanroomError,
    UnsupportedCommandError,
)
from app.cleanroom.events import EventLog, EventType
from app.cleanroom.state import SessionState, SessionStateMachine

if TYPE_CHECKING:
    from app.cleanroom.transport import Transport

logger = logging.getLogger(__name__)


class Session:
    """Lifecycle controller combining transport, state machine, and dispatch.

    This controller is runnable only inside tests or explicit development
    code. It must not expose:
    - a production CLI
    - a Windows service entry point
    - a named-pipe endpoint
    - a network listener
    - an auto-start path
    - an installer
    - an executable package
    """

    def __init__(
        self,
        transport: Transport,
        catalog: CommandCatalog | None = None,
        event_log: EventLog | None = None,
    ) -> None:
        self._transport = transport
        self._catalog = catalog or CommandCatalog()
        self._event_log = event_log or EventLog()
        self._state_machine = SessionStateMachine()
        self._dispatcher = Dispatcher(
            self._catalog, self._state_machine, self._event_log
        )

    @property
    def state(self) -> SessionState:
        """Current session state."""
        return self._state_machine.state

    @property
    def transport(self) -> Transport:
        """The underlying transport."""
        return self._transport

    @property
    def dispatcher(self) -> Dispatcher:
        """The command dispatcher."""
        return self._dispatcher

    @property
    def event_log(self) -> EventLog:
        """The event log."""
        return self._event_log

    def register_handler(
        self,
        message_type: int,
        handler: HandlerFunc,
    ) -> None:
        """Register a handler for a message type.

        Args:
            message_type: Numeric message type identifier.
            handler: Async handler function.
        """
        self._dispatcher.register(message_type, handler)

    async def open(self) -> None:
        """Open the session transport and transition state.

        Raises:
            CleanroomError: If open fails.
        """
        await self._transport.open()
        self._state_machine.open_transport()
        self._event_log.record(
            EventType.TRANSPORT_OPENED,
            source="session",
        )

    async def close(self) -> None:
        """Close the session transport and transition state.

        Always attempts cleanup even if transport close fails.
        If already in CLOSED state, only closes transport.
        If in FAILED state, only closes transport.
        If in any other state, transitions to FAILED (fail-safe).
        """
        try:
            await self._transport.close()
        except Exception:
            logger.exception("Error closing transport")
        finally:
            if self._state_machine.state == SessionState.CLOSED or self._state_machine.is_terminal():
                self._event_log.record(
                    EventType.TRANSPORT_CLOSED,
                    source="session",
                )
            else:
                self._state_machine.fail()
                self._event_log.record(
                    EventType.SESSION_FAILED,
                    source="session",
                )
                self._event_log.record(
                    EventType.TRANSPORT_CLOSED,
                    source="session",
                )

    async def handle_client_start(self) -> None:
        """Handle receipt of LCOMMAND_CLIENT_START.

        Transitions:
        - TRANSPORT_OPEN → START_PENDING
        - START_PENDING → ACTIVE (after reply)

        Raises:
            CleanroomError: If handling fails.
        """
        self._state_machine.receive_client_start()
        self._event_log.record(
            EventType.TRANSITION_ACCEPTED,
            source="session",
            details={"transition": "client_start_received"},
        )
        # In a real implementation, we would send SCOMMAND_CLIENT_START_REPLY
        # For G17 synthetic foundation, we transition directly to ACTIVE
        self._state_machine.send_start_reply()
        self._event_log.record(
            EventType.TRANSITION_ACCEPTED,
            source="session",
            details={"transition": "start_reply_sent"},
        )

    async def handle_client_end(self) -> None:
        """Handle receipt of LCOMMAND_CLIENT_END.

        Transitions:
        - ACTIVE → END_PENDING → CLOSED

        Raises:
            CleanroomError: If handling fails.
        """
        self._state_machine.receive_client_end()
        self._event_log.record(
            EventType.TRANSITION_ACCEPTED,
            source="session",
            details={"transition": "client_end_received"},
        )
        self._state_machine.close()
        self._event_log.record(
            EventType.TRANSITION_ACCEPTED,
            source="session",
            details={"transition": "session_closed"},
        )
        await self._transport.close()
        self._event_log.record(
            EventType.TRANSPORT_CLOSED,
            source="session",
        )

    async def send_cert_error(self) -> None:
        """Send SCOMMAND_CERT_ERROR.

        This is a synthetic error notification. In the clean-room
        foundation, it transitions to FAILED state.

        Evidence: CERT_ERROR identity confirmed by G16, but payload
        semantics and state effects are NOT confirmed. This method
        represents the minimal synthetic model only.
        """
        self._state_machine.fail()
        self._event_log.record(
            EventType.SESSION_FAILED,
            source="session",
            details={"error_type": "cert_error"},
        )

    async def send_nw_error(self) -> None:
        """Send SCOMMAND_NW_ERROR.

        This is a synthetic error notification. In the clean-room
        foundation, it transitions to FAILED state.

        Evidence: NW_ERROR identity confirmed by G16, but payload
        semantics and state effects are NOT confirmed. This method
        represents the minimal synthetic model only.
        """
        self._state_machine.fail()
        self._event_log.record(
            EventType.SESSION_FAILED,
            source="session",
            details={"error_type": "nw_error"},
        )

    async def send_nwrecover_notice(self) -> None:
        """Send SCOMMAND_NWRECOVER_NOTICE.

        This is a synthetic recovery notification. In the clean-room
        foundation, it records the event but does not change state.

        Evidence: NWRECOVER_NOTICE identity confirmed by G16, but payload
        semantics and state effects are NOT confirmed. This method
        represents the minimal synthetic model only.
        """
        self._event_log.record(
            EventType.SYNTHETIC_DISCONNECT,
            source="session",
            details={"notice_type": "nwrecover"},
        )

    async def process_frame(
        self,
        message_type: int,
        packet_id: int,
        message_name: str,
        payload: bytes,
    ) -> bytes | None:
        """Process a single frame through the dispatcher.

        Args:
            message_type: Numeric message type.
            packet_id: Packet identifier.
            message_name: Symbolic message name.
            payload: Raw payload bytes.

        Returns:
            Response bytes or None.
        """
        self._event_log.record(
            EventType.FRAME_RECEIVED,
            source="session",
            details={"message_type": message_type},
        )
        return await self._dispatcher.dispatch(
            message_type, packet_id, message_name, payload
        )

    async def run_lifecycle(
        self,
        commands: list[tuple[int, int, str, bytes]],
    ) -> list[bytes | None]:
        """Run a complete lifecycle with the given commands.

        This is the primary integration test entry point.

        Lifecycle commands (LCOMMAND_CLIENT_START, LCOMMAND_CLIENT_END)
        are dispatched by symbolic name, not numeric ID, because their
        numeric_id is None in the catalog (not confirmed by G16 evidence).

        Args:
            commands: List of (message_type, packet_id, message_name, payload).
                For lifecycle commands, message_name is used for dispatch.
                message_type is ignored for lifecycle commands.

        Returns:
            List of responses from each command.
        """
        responses: list[bytes | None] = []

        await self.open()

        for message_type, packet_id, message_name, payload in commands:
            try:
                if message_name == "LCOMMAND_CLIENT_START":
                    await self.handle_client_start()
                    responses.append(None)
                elif message_name == "LCOMMAND_CLIENT_END":
                    await self.handle_client_end()
                    responses.append(None)
                else:
                    response = await self.process_frame(
                        message_type, packet_id, message_name, payload
                    )
                    responses.append(response)
            except UnsupportedCommandError:
                responses.append(None)
            except CleanroomError:
                responses.append(None)

        return responses
