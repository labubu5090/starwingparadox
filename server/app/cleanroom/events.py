"""Observability events for clean-room protocol foundation.

All events are structured, deterministic, and suitable for test
assertions. No raw unknown payload logging, no credentials, no
certificate data, no personal data, no production hostnames.
"""
from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Any


class EventType(enum.Enum):
    """Categories of observable events."""

    TRANSPORT_OPENED = "transport_opened"
    TRANSPORT_CLOSED = "transport_closed"
    FRAME_RECEIVED = "frame_received"
    FRAME_SENT = "frame_sent"
    TRANSITION_ACCEPTED = "transition_accepted"
    TRANSITION_REJECTED = "transition_rejected"
    UNSUPPORTED_COMMAND = "unsupported_command"
    SYNTHETIC_TIMEOUT = "synthetic_timeout"
    SYNTHETIC_DISCONNECT = "synthetic_disconnect"
    SESSION_FAILED = "session_failed"


@dataclass(frozen=True)
class Event:
    """A single observable event.

    Attributes:
        event_type: Category of the event.
        timestamp: Event timestamp (monotonic).
        source: Source module or component.
        details: Event-specific details (no secrets).
    """

    event_type: EventType
    timestamp: float = field(default_factory=time.monotonic)
    source: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class EventLog:
    """Collects events for test assertions and diagnostics.

    Events are stored in memory only. No filesystem side effects.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    def record(
        self,
        event_type: EventType,
        *,
        source: str = "",
        details: dict[str, Any] | None = None,
    ) -> Event:
        """Record an event.

        Args:
            event_type: Category of the event.
            source: Source module or component.
            details: Event-specific details (no secrets).

        Returns:
            The recorded event.
        """
        event = Event(
            event_type=event_type,
            source=source,
            details=details or {},
        )
        self._events.append(event)
        return event

    def get_events(self) -> list[Event]:
        """Return all recorded events.

        Returns:
            List of recorded events.
        """
        return list(self._events)

    def get_events_by_type(self, event_type: EventType) -> list[Event]:
        """Return events matching the given type.

        Args:
            event_type: Event type to filter by.

        Returns:
            List of matching events.
        """
        return [e for e in self._events if e.event_type == event_type]

    def clear(self) -> None:
        """Clear all recorded events."""
        self._events.clear()

    def count(self) -> int:
        """Return the number of recorded events.

        Returns:
            Event count.
        """
        return len(self._events)
