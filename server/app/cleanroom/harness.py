"""Session scenario harness for clean-room protocol foundation.

This module provides a harness for running synthetic scenarios
against the session lifecycle. All scenarios are documented with
their evidence level and constraints.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from app.cleanroom.session import Session
from app.cleanroom.synthetic_transport import SyntheticTransport


class ScenarioEvidenceLevel(enum.Enum):
    """Evidence level for scenarios."""

    CONFIRMED = "confirmed"
    ELIGIBLE = "eligible"
    SYNTHETIC = "synthetic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ScenarioStep:
    """A single step in a scenario.

    Attributes:
        step_id: Unique step identifier.
        action: Action to perform.
        args: Action arguments.
        expected_state: Expected state after step (None = no check).
        expected_events: Expected event types after step.
        evidence_level: Evidence classification.
        description: Human-readable description.
    """

    step_id: str
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    expected_state: str | None = None
    expected_events: list[str] = field(default_factory=list)
    evidence_level: ScenarioEvidenceLevel = ScenarioEvidenceLevel.SYNTHETIC
    description: str = ""


@dataclass(frozen=True)
class ScenarioResult:
    """Result of running a scenario step.

    Attributes:
        step_id: Step identifier.
        success: Whether step succeeded.
        actual_state: Actual state after step.
        actual_events: Actual events after step.
        error: Error message if step failed.
    """

    step_id: str
    success: bool
    actual_state: str
    actual_events: list[str]
    error: str | None = None


@dataclass(frozen=True)
class ScenarioDefinition:
    """Definition of a synthetic scenario.

    Attributes:
        scenario_id: Unique scenario identifier.
        name: Human-readable scenario name.
        description: Scenario description.
        steps: List of scenario steps.
        evidence_level: Evidence classification.
        source: Evidence source reference.
        constraints: Known constraints or limitations.
    """

    scenario_id: str
    name: str
    description: str
    steps: list[ScenarioStep]
    evidence_level: ScenarioEvidenceLevel
    source: str
    constraints: str = ""


class ScenarioHarness:
    """Harness for running synthetic scenarios.

    This harness:
    - executes scenarios against the session lifecycle
    - records results for test assertions
    - documents evidence levels for all scenarios
    - never assumes production behavior
    """

    def __init__(self) -> None:
        """Initialize the harness."""
        self._scenarios: dict[str, ScenarioDefinition] = {}
        self._results: list[ScenarioResult] = []

    def register_scenario(self, scenario: ScenarioDefinition) -> None:
        """Register a scenario definition.

        Args:
            scenario: Scenario definition to register.

        Raises:
            ValueError: If scenario ID already registered.
        """
        if scenario.scenario_id in self._scenarios:
            raise ValueError(
                f"Scenario already registered: {scenario.scenario_id}"
            )
        self._scenarios[scenario.scenario_id] = scenario

    def get_scenario(self, scenario_id: str) -> ScenarioDefinition | None:
        """Get a scenario by ID.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            ScenarioDefinition or None.
        """
        return self._scenarios.get(scenario_id)

    def get_all_scenarios(self) -> list[ScenarioDefinition]:
        """Return all registered scenarios.

        Returns:
            List of ScenarioDefinition instances.
        """
        return list(self._scenarios.values())

    async def run_scenario(
        self,
        scenario_id: str,
    ) -> list[ScenarioResult]:
        """Run a scenario and return results.

        Args:
            scenario_id: Scenario identifier.

        Returns:
            List of ScenarioResult instances.

        Raises:
            KeyError: If scenario not found.
        """
        scenario = self._scenarios.get(scenario_id)
        if scenario is None:
            raise KeyError(f"Scenario not found: {scenario_id}")

        transport = SyntheticTransport()
        session = Session(transport)

        results: list[ScenarioResult] = []

        for step in scenario.steps:
            result = await self._run_step(session, step)
            results.append(result)

            if not result.success:
                break

        self._results.extend(results)
        return results

    async def _run_step(
        self,
        session: Session,
        step: ScenarioStep,
    ) -> ScenarioResult:
        """Run a single scenario step.

        Args:
            session: Session instance.
            step: Step to run.

        Returns:
            ScenarioResult for the step.
        """
        try:
            if step.action == "open":
                await session.open()
            elif step.action == "close":
                await session.close()
            elif step.action == "handle_client_start":
                await session.handle_client_start()
            elif step.action == "handle_client_end":
                await session.handle_client_end()
            elif step.action == "send_cert_error":
                await session.send_cert_error()
            elif step.action == "send_nw_error":
                await session.send_nw_error()
            elif step.action == "send_nwrecover_notice":
                await session.send_nwrecover_notice()
            else:
                return ScenarioResult(
                    step_id=step.step_id,
                    success=False,
                    actual_state=session.state.value,
                    actual_events=[],
                    error=f"Unknown action: {step.action}",
                )

            actual_state = session.state.value
            actual_events = [
                e.event_type.value
                for e in session.event_log.get_events()
            ]

            state_ok = (
                step.expected_state is None
                or actual_state == step.expected_state
            )

            events_ok = True
            if step.expected_events:
                for expected in step.expected_events:
                    if expected not in actual_events:
                        events_ok = False
                        break

            success = state_ok and events_ok

            return ScenarioResult(
                step_id=step.step_id,
                success=success,
                actual_state=actual_state,
                actual_events=actual_events,
                error=None if success else (
                    f"State: expected {step.expected_state}, got {actual_state}"
                    if not state_ok
                    else f"Missing expected events: {step.expected_events}"
                ),
            )

        except Exception as e:
            return ScenarioResult(
                step_id=step.step_id,
                success=False,
                actual_state=session.state.value,
                actual_events=[],
                error=str(e),
            )

    def get_results(self) -> list[ScenarioResult]:
        """Return all recorded results.

        Returns:
            List of ScenarioResult instances.
        """
        return list(self._results)

    def clear_results(self) -> None:
        """Clear all recorded results."""
        self._results.clear()
