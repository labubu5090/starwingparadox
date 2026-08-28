"""Deterministic session state machine for clean-room protocol foundation.

This module implements only the confirmed synthetic lifecycle from G16.
Invalid transitions fail closed. State mutation occurs only through
explicit methods.
"""
from __future__ import annotations

import enum

from app.cleanroom.errors import (
    CommandAfterEndError,
    CommandBeforeStartError,
    DuplicateStartError,
    InvalidTransitionError,
)


class SessionState(enum.Enum):
    """States of the session lifecycle.

    These represent the confirmed synthetic lifecycle:
    CREATED → TRANSPORT_OPEN → START_PENDING → ACTIVE → END_PENDING → CLOSED
    """

    CREATED = "created"
    TRANSPORT_OPEN = "transport_open"
    START_PENDING = "start_pending"
    ACTIVE = "active"
    END_PENDING = "end_pending"
    CLOSED = "closed"
    FAILED = "failed"


# Confirmed transitions from G16 evidence
_ALLOWED_TRANSITIONS: dict[SessionState, set[SessionState]] = {
    SessionState.CREATED: {SessionState.TRANSPORT_OPEN, SessionState.FAILED},
    SessionState.TRANSPORT_OPEN: {
        SessionState.START_PENDING,
        SessionState.FAILED,
        SessionState.CLOSED,
    },
    SessionState.START_PENDING: {
        SessionState.ACTIVE,
        SessionState.FAILED,
        SessionState.CLOSED,
    },
    SessionState.ACTIVE: {
        SessionState.END_PENDING,
        SessionState.FAILED,
        SessionState.CLOSED,
    },
    SessionState.END_PENDING: {SessionState.CLOSED, SessionState.FAILED},
    SessionState.CLOSED: set(),
    SessionState.FAILED: set(),
}


class SessionStateMachine:
    """Deterministic pure state machine for the confirmed lifecycle.

    Requirements:
    - invalid transitions fail closed
    - transition function is deterministic
    - state mutation occurs only through explicit methods
    - duplicate start is rejected
    - command before transport open is rejected
    - command after close is rejected
    - unknown commands do not advance lifecycle
    - timeout produces explicit failure or closure
    - disconnect cannot leave an apparently active session
    - error state is observable
    """

    def __init__(self) -> None:
        self._state = SessionState.CREATED
        self._transition_history: list[tuple[SessionState, SessionState]] = []

    @property
    def state(self) -> SessionState:
        """Current session state."""
        return self._state

    @property
    def transition_history(self) -> list[tuple[SessionState, SessionState]]:
        """History of state transitions."""
        return list(self._transition_history)

    def can_transition(self, target: SessionState) -> bool:
        """Check if a transition to the target state is allowed.

        Args:
            target: Target state.

        Returns:
            True if transition is allowed.
        """
        return target in _ALLOWED_TRANSITIONS.get(self._state, set())

    def transition(self, target: SessionState) -> None:
        """Execute a state transition.

        Args:
            target: Target state.

        Raises:
            InvalidTransitionError: If transition is not allowed.
        """
        if not self.can_transition(target):
            raise InvalidTransitionError(
                f"Cannot transition from {self._state.value} to {target.value}"
            )
        self._transition_history.append((self._state, target))
        self._state = target

    def open_transport(self) -> None:
        """Transition to TRANSPORT_OPEN.

        Raises:
            InvalidTransitionError: If transition is not allowed.
        """
        self.transition(SessionState.TRANSPORT_OPEN)

    def receive_client_start(self) -> None:
        """Handle receipt of LCOMMAND_CLIENT_START.

        Transitions:
        - TRANSPORT_OPEN → START_PENDING (first start)
        - Duplicate start → DuplicateStartError
        - Before open → CommandBeforeStartError

        Raises:
            DuplicateStartError: If already started.
            CommandBeforeStartError: If transport not open.
            InvalidTransitionError: If transition is not allowed.
        """
        if self._state in (SessionState.START_PENDING, SessionState.ACTIVE):
            raise DuplicateStartError(
                "SESSION_START already received"
            )
        if self._state != SessionState.TRANSPORT_OPEN:
            raise CommandBeforeStartError(
                f"Cannot start in state {self._state.value}"
            )
        self.transition(SessionState.START_PENDING)

    def send_start_reply(self) -> None:
        """Transition to ACTIVE after sending SCOMMAND_CLIENT_START_REPLY.

        Raises:
            InvalidTransitionError: If transition is not allowed.
        """
        self.transition(SessionState.ACTIVE)

    def receive_client_end(self) -> None:
        """Handle receipt of LCOMMAND_CLIENT_END.

        Transitions:
        - ACTIVE → END_PENDING
        - Before active → CommandBeforeStartError

        Raises:
            CommandBeforeStartError: If not active.
            InvalidTransitionError: If transition is not allowed.
        """
        if self._state not in (SessionState.ACTIVE, SessionState.END_PENDING):
            raise CommandBeforeStartError(
                f"Cannot end in state {self._state.value}"
            )
        self.transition(SessionState.END_PENDING)

    def close(self) -> None:
        """Transition to CLOSED.

        Raises:
            InvalidTransitionError: If transition is not allowed.
        """
        self.transition(SessionState.CLOSED)

    def fail(self) -> None:
        """Transition to FAILED from any non-terminal state.

        Always succeeds unless already in CLOSED or FAILED.
        """
        if self._state not in (SessionState.CLOSED, SessionState.FAILED):
            self._transition_history.append((self._state, SessionState.FAILED))
            self._state = SessionState.FAILED

    def validate_command_allowed(self) -> None:
        """Validate that a command can be received in the current state.

        Raises:
            CommandBeforeStartError: If transport not open.
            CommandAfterEndError: If session ended.
        """
        if self._state in (SessionState.CLOSED, SessionState.FAILED):
            raise CommandAfterEndError(
                f"Command received in terminal state {self._state.value}"
            )
        if self._state == SessionState.CREATED:
            raise CommandBeforeStartError(
                "Command received before transport open"
            )

    def is_terminal(self) -> bool:
        """Check if the session is in a terminal state.

        Returns:
            True if CLOSED or FAILED.
        """
        return self._state in (SessionState.CLOSED, SessionState.FAILED)

    def reset(self) -> None:
        """Reset the state machine to CREATED.

        For testing only.
        """
        self._state = SessionState.CREATED
        self._transition_history.clear()
