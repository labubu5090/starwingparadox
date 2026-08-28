"""State-machine invariant checker for clean-room protocol foundation.

This module provides checks that verify state-machine invariants
are maintained throughout the session lifecycle.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass

from app.cleanroom.state import SessionState, SessionStateMachine


class InvariantLevel(enum.Enum):
    """Evidence level for invariants."""

    CONFIRMED = "confirmed"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class InvariantCheck:
    """Result of an invariant check.

    Attributes:
        name: Invariant name.
        passed: Whether check passed.
        level: Evidence level.
        details: Additional details.
    """

    name: str
    passed: bool
    level: InvariantLevel
    details: str = ""


class StateMachineInvariantChecker:
    """Checker for state-machine invariants.

    This checker verifies:
    - Terminal states have no outgoing transitions
    - State transitions are deterministic
    - Transition history is maintained
    - Fail always produces a terminal state
    - Reset clears history
    """

    def check_terminal_no_outgoing(
        self,
        sm: SessionStateMachine,
    ) -> InvariantCheck:
        """Check that terminal states have no outgoing transitions.

        Args:
            sm: State machine to check.

        Returns:
            InvariantCheck result.
        """
        original_state = sm.state

        for terminal in (SessionState.CLOSED, SessionState.FAILED):
            sm._state = terminal
            for target in SessionState:
                if target == terminal:
                    continue
                try:
                    sm.transition(target)
                    sm._state = original_state
                    return InvariantCheck(
                        name="terminal_no_outgoing",
                        passed=False,
                        level=InvariantLevel.CONFIRMED,
                        details=(
                            f"Terminal state {terminal.value} allowed "
                            f"transition to {target.value}"
                        ),
                    )
                except Exception:
                    pass

            sm._state = original_state

        return InvariantCheck(
            name="terminal_no_outgoing",
            passed=True,
            level=InvariantLevel.CONFIRMED,
            details="Terminal states have no outgoing transitions",
        )

    def check_deterministic_transitions(
        self,
        sm: SessionStateMachine,
    ) -> InvariantCheck:
        """Check that transitions are deterministic.

        Args:
            sm: State machine to check.

        Returns:
            InvariantCheck result.
        """
        original_state = sm.state
        original_history = list(sm.transition_history)

        for state in SessionState:
            sm._state = state
            sm._transition_history = []

            for target in SessionState:
                try:
                    sm.transition(target)
                    result1 = sm.state
                    sm._state = state
                    sm._transition_history = []

                    sm.transition(target)
                    result2 = sm.state

                    sm._state = state
                    sm._transition_history = []

                    if result1 != result2:
                        return InvariantCheck(
                            name="deterministic_transitions",
                            passed=False,
                            level=InvariantLevel.SYNTHETIC,
                            details=(
                                f"Transition from {state.value} to "
                                f"{target.value} not deterministic"
                            ),
                        )
                except Exception:
                    pass

        sm._state = original_state
        sm._transition_history = original_history

        return InvariantCheck(
            name="deterministic_transitions",
            passed=True,
            level=InvariantLevel.SYNTHETIC,
            details="All transitions are deterministic",
        )

    def check_transition_history_maintained(
        self,
        sm: SessionStateMachine,
    ) -> InvariantCheck:
        """Check that transition history is maintained.

        Args:
            sm: State machine to check.

        Returns:
            InvariantCheck result.
        """
        original_state = sm.state
        original_history = list(sm.transition_history)

        sm._state = SessionState.CREATED
        sm._transition_history = []

        sm.open_transport()
        if len(sm.transition_history) != 1:
            sm._state = original_state
            sm._transition_history = original_history
            return InvariantCheck(
                name="transition_history_maintained",
                passed=False,
                level=InvariantLevel.CONFIRMED,
                details="History not maintained after open_transport",
            )

        sm.receive_client_start()
        if len(sm.transition_history) != 2:
            sm._state = original_state
            sm._transition_history = original_history
            return InvariantCheck(
                name="transition_history_maintained",
                passed=False,
                level=InvariantLevel.CONFIRMED,
                details="History not maintained after receive_client_start",
            )

        sm._state = original_state
        sm._transition_history = original_history

        return InvariantCheck(
            name="transition_history_maintained",
            passed=True,
            level=InvariantLevel.CONFIRMED,
            details="Transition history is maintained",
        )

    def check_fail_always_terminal(
        self,
        sm: SessionStateMachine,
    ) -> InvariantCheck:
        """Check that fail always produces a terminal state.

        Note: fail() from CLOSED or FAILED does nothing (already terminal).
        This is correct behavior - we only check non-terminal states.

        Args:
            sm: State machine to check.

        Returns:
            InvariantCheck result.
        """
        original_state = sm.state
        original_history = list(sm.transition_history)

        non_terminal_states = [
            SessionState.CREATED,
            SessionState.TRANSPORT_OPEN,
            SessionState.START_PENDING,
            SessionState.ACTIVE,
            SessionState.END_PENDING,
        ]

        for state in non_terminal_states:
            sm._state = state
            sm._transition_history = []

            sm.fail()

            if sm.state != SessionState.FAILED:
                sm._state = original_state
                sm._transition_history = original_history
                return InvariantCheck(
                    name="fail_always_terminal",
                    passed=False,
                    level=InvariantLevel.CONFIRMED,
                    details=f"fail() from {state.value} did not produce FAILED",
                )

        sm._state = original_state
        sm._transition_history = original_history

        return InvariantCheck(
            name="fail_always_terminal",
            passed=True,
            level=InvariantLevel.CONFIRMED,
            details="fail() always produces terminal state from non-terminal states",
        )

    def check_reset_clears_history(
        self,
        sm: SessionStateMachine,
    ) -> InvariantCheck:
        """Check that reset clears history.

        Args:
            sm: State machine to check.

        Returns:
            InvariantCheck result.
        """
        original_state = sm.state

        sm._state = SessionState.CREATED
        sm._transition_history = []

        sm.open_transport()
        sm.receive_client_start()

        if len(sm.transition_history) == 0:
            sm._state = original_state
            return InvariantCheck(
                name="reset_clears_history",
                passed=False,
                level=InvariantLevel.SYNTHETIC,
                details="No history to clear",
            )

        sm.reset()

        if len(sm.transition_history) != 0:
            sm._state = original_state
            return InvariantCheck(
                name="reset_clears_history",
                passed=False,
                level=InvariantLevel.SYNTHETIC,
                details="reset() did not clear history",
            )

        if sm.state != SessionState.CREATED:
            sm._state = original_state
            return InvariantCheck(
                name="reset_clears_history",
                passed=False,
                level=InvariantLevel.SYNTHETIC,
                details="reset() did not reset state to CREATED",
            )

        sm._state = original_state

        return InvariantCheck(
            name="reset_clears_history",
            passed=True,
            level=InvariantLevel.SYNTHETIC,
            details="reset() clears history and resets state",
        )

    def check_all_invariants(
        self,
        sm: SessionStateMachine,
    ) -> list[InvariantCheck]:
        """Run all invariant checks.

        Args:
            sm: State machine to check.

        Returns:
            List of InvariantCheck results.
        """
        return [
            self.check_terminal_no_outgoing(sm),
            self.check_deterministic_transitions(sm),
            self.check_transition_history_maintained(sm),
            self.check_fail_always_terminal(sm),
            self.check_reset_clears_history(sm),
        ]
