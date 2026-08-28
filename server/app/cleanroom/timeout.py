"""Deterministic clock and timeout model for clean-room protocol foundation.

This module provides a deterministic time source for tests and a timeout
model that documents what is confirmed vs inferred.

Timeout evidence:
- PING timeout: NOT confirmed (G16 observed ping/pong but no timeout values)
- Session timeout: NOT confirmed (G16 observed session lifecycle but no timeout)
- Error timeout: NOT confirmed (G16 observed error commands but no timeout)

All timeout values in this module are synthetic defaults for testing only.
They do NOT represent observed production behavior.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass


class TimeoutEvidenceLevel(enum.Enum):
    """Evidence level for timeout values."""

    CONFIRMED = "confirmed"
    INFERRED = "inferred"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TimeoutRecord:
    """Documents the evidence level for a timeout value.

    Attributes:
        name: Timeout name.
        value_ms: Timeout value in milliseconds.
        evidence_level: Evidence classification.
        source: Evidence source reference.
        constraints: Known constraints or limitations.
    """

    name: str
    value_ms: int
    evidence_level: TimeoutEvidenceLevel
    source: str
    constraints: str = ""


class DeterministicClock:
    """Deterministic clock for tests.

    This clock can be advanced manually to trigger timeouts
    without real time passing. Suitable for deterministic tests.
    """

    def __init__(self, initial_time: float = 0.0) -> None:
        """Initialize the clock.

        Args:
            initial_time: Initial time in seconds.
        """
        self._time = initial_time

    def now(self) -> float:
        """Return the current clock time.

        Returns:
            Current time in seconds.
        """
        return self._time

    def advance(self, seconds: float) -> None:
        """Advance the clock by the given number of seconds.

        Args:
            seconds: Seconds to advance (must be non-negative).
        """
        if seconds < 0:
            raise ValueError("Cannot advance clock by negative time")
        self._time += seconds

    def reset(self, initial_time: float = 0.0) -> None:
        """Reset the clock to the given time.

        Args:
            initial_time: Time to reset to in seconds.
        """
        self._time = initial_time


class SyntheticTimeoutModel:
    """Timeout model with evidence-locked constraints.

    This model:
    - documents evidence levels for all timeout values
    - uses deterministic clock for testing
    - never assumes production timeout behavior
    - provides synthetic defaults for testing

    Default timeout values:
    - PING_INTERVAL_MS: 30000ms (synthetic, no evidence)
    - PING_TIMEOUT_MS: 5000ms (synthetic, no evidence)
    - SESSION_TIMEOUT_MS: 300000ms (synthetic, no evidence)
    - ERROR_TIMEOUT_MS: 1000ms (synthetic, no evidence)
    """

    DEFAULT_TIMEOUT_RECORDS = [
        TimeoutRecord(
            name="PING_INTERVAL_MS",
            value_ms=30000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="Synthetic default, no G16 evidence",
            constraints="Used for ping scheduling in tests only",
        ),
        TimeoutRecord(
            name="PING_TIMEOUT_MS",
            value_ms=5000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="Synthetic default, no G16 evidence",
            constraints="Used for ping response timeout in tests only",
        ),
        TimeoutRecord(
            name="SESSION_TIMEOUT_MS",
            value_ms=300000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="Synthetic default, no G16 evidence",
            constraints="Used for session idle timeout in tests only",
        ),
        TimeoutRecord(
            name="ERROR_TIMEOUT_MS",
            value_ms=1000,
            evidence_level=TimeoutEvidenceLevel.SYNTHETIC,
            source="Synthetic default, no G16 evidence",
            constraints="Used for error notification delay in tests only",
        ),
    ]

    def __init__(
        self,
        clock: DeterministicClock | None = None,
        custom_timeouts: dict[str, int] | None = None,
    ) -> None:
        """Initialize the timeout model.

        Args:
            clock: Deterministic clock instance.
            custom_timeouts: Custom timeout values in milliseconds.
                Overrides defaults for matching names.
        """
        self._clock = clock or DeterministicClock()
        self._timeout_records: dict[str, TimeoutRecord] = {}
        self._timers: dict[str, float] = {}

        for record in self.DEFAULT_TIMEOUT_RECORDS:
            self._timeout_records[record.name] = record

        if custom_timeouts:
            for name, value_ms in custom_timeouts.items():
                if name in self._timeout_records:
                    existing = self._timeout_records[name]
                    self._timeout_records[name] = TimeoutRecord(
                        name=name,
                        value_ms=value_ms,
                        evidence_level=existing.evidence_level,
                        source=existing.source,
                        constraints=existing.constraints,
                    )

    def get_timeout(self, name: str) -> int:
        """Get a timeout value by name.

        Args:
            name: Timeout name.

        Returns:
            Timeout value in milliseconds.

        Raises:
            KeyError: If timeout name not found.
        """
        if name not in self._timeout_records:
            raise KeyError(f"Unknown timeout: {name}")
        return self._timeout_records[name].value_ms

    def get_timeout_record(self, name: str) -> TimeoutRecord:
        """Get a timeout record by name.

        Args:
            name: Timeout name.

        Returns:
            TimeoutRecord instance.

        Raises:
            KeyError: If timeout name not found.
        """
        if name not in self._timeout_records:
            raise KeyError(f"Unknown timeout: {name}")
        return self._timeout_records[name]

    def get_all_records(self) -> list[TimeoutRecord]:
        """Return all timeout records.

        Returns:
            List of TimeoutRecord instances.
        """
        return list(self._timeout_records.values())

    def start_timer(self, name: str) -> None:
        """Start a timer for the given timeout.

        Args:
            name: Timeout name.

        Raises:
            KeyError: If timeout name not found.
        """
        if name not in self._timeout_records:
            raise KeyError(f"Unknown timeout: {name}")
        self._timers[name] = self._clock.now()

    def is_expired(self, name: str) -> bool:
        """Check if a timer has expired.

        Args:
            name: Timer name.

        Returns:
            True if timer has expired.

        Raises:
            KeyError: If timer not started.
        """
        if name not in self._timers:
            raise KeyError(f"Timer not started: {name}")

        start_time = self._timers[name]
        timeout_ms = self._timeout_records[name].value_ms
        elapsed_ms = (self._clock.now() - start_time) * 1000
        return elapsed_ms >= timeout_ms

    def reset_timer(self, name: str) -> None:
        """Reset a timer.

        Args:
            name: Timer name.
        """
        self._timers.pop(name, None)

    def clear_all_timers(self) -> None:
        """Clear all timers."""
        self._timers.clear()
