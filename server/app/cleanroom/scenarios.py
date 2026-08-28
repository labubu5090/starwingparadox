"""Versioned synthetic scenarios for clean-room protocol foundation.

This module defines versioned synthetic scenarios that document
the evidence level and constraints for each scenario.

All scenarios are synthetic and do NOT represent observed production
behavior. They are used for testing the clean-room foundation only.
"""
from __future__ import annotations

from app.cleanroom.harness import (
    ScenarioDefinition,
    ScenarioEvidenceLevel,
    ScenarioStep,
)

SCENARIO_VERSION = "1.0.0"


def _create_happy_path_lifecycle() -> ScenarioDefinition:
    """Create the happy-path lifecycle scenario.

    Evidence: Synthetic. Documents the confirmed lifecycle states
    but NOT the observed timing or payload semantics.
    """
    return ScenarioDefinition(
        scenario_id="happy_path_lifecycle",
        name="Happy Path Lifecycle",
        description=(
            "Complete lifecycle from open to close with start and end. "
            "Evidence: SYNTHETIC. Lifecycle states are confirmed by G16, "
            "but timing and payload semantics are NOT confirmed."
        ),
        steps=[
            ScenarioStep(
                step_id="open",
                action="open",
                expected_state="transport_open",
                expected_events=["transport_opened"],
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Open transport (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_start",
                action="handle_client_start",
                expected_state="active",
                expected_events=[
                    "transition_accepted",
                    "transition_accepted",
                ],
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_START (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_end",
                action="handle_client_end",
                expected_state="closed",
                expected_events=[
                    "transition_accepted",
                    "transition_accepted",
                    "transport_closed",
                ],
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_END (CONFIRMED by G16)",
            ),
        ],
        evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
        source="G16 confirmed lifecycle states, synthetic timing",
        constraints="Timing and payload semantics are NOT confirmed",
    )


def _create_error_path_cert_error() -> ScenarioDefinition:
    """Create the cert error path scenario.

    Evidence: SYNTHETIC. CERT_ERROR identity is confirmed by G16,
    but payload semantics and state effects are NOT confirmed.
    """
    return ScenarioDefinition(
        scenario_id="error_path_cert_error",
        name="Cert Error Path",
        description=(
            "Session open, start, then cert error. "
            "Evidence: SYNTHETIC. CERT_ERROR identity confirmed, "
            "but payload semantics and state effects NOT confirmed."
        ),
        steps=[
            ScenarioStep(
                step_id="open",
                action="open",
                expected_state="transport_open",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Open transport (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_start",
                action="handle_client_start",
                expected_state="active",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_START (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="cert_error",
                action="send_cert_error",
                expected_state="failed",
                expected_events=["session_failed"],
                evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
                description="Send CERT_ERROR (identity CONFIRMED, effects SYNTHETIC)",
            ),
        ],
        evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
        source="G16 confirmed CERT_ERROR identity, synthetic state effects",
        constraints="Cert error state effects are NOT confirmed",
    )


def _create_error_path_nw_error() -> ScenarioDefinition:
    """Create the network error path scenario.

    Evidence: SYNTHETIC. NW_ERROR identity is confirmed by G16,
    but payload semantics and state effects are NOT confirmed.
    """
    return ScenarioDefinition(
        scenario_id="error_path_nw_error",
        name="Network Error Path",
        description=(
            "Session open, start, then network error. "
            "Evidence: SYNTHETIC. NW_ERROR identity confirmed, "
            "but payload semantics and state effects NOT confirmed."
        ),
        steps=[
            ScenarioStep(
                step_id="open",
                action="open",
                expected_state="transport_open",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Open transport (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_start",
                action="handle_client_start",
                expected_state="active",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_START (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="nw_error",
                action="send_nw_error",
                expected_state="failed",
                expected_events=["session_failed"],
                evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
                description="Send NW_ERROR (identity CONFIRMED, effects SYNTHETIC)",
            ),
        ],
        evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
        source="G16 confirmed NW_ERROR identity, synthetic state effects",
        constraints="Network error state effects are NOT confirmed",
    )


def _create_recovery_path_nwrecover() -> ScenarioDefinition:
    """Create the network recovery path scenario.

    Evidence: SYNTHETIC. NWRECOVER_NOTICE identity is confirmed by G16,
    but payload semantics and state effects are NOT confirmed.
    """
    return ScenarioDefinition(
        scenario_id="recovery_path_nwrecover",
        name="Network Recovery Path",
        description=(
            "Session open, start, network error, then recovery notice. "
            "Evidence: SYNTHETIC. NWRECOVER_NOTICE identity confirmed, "
            "but payload semantics and state effects NOT confirmed."
        ),
        steps=[
            ScenarioStep(
                step_id="open",
                action="open",
                expected_state="transport_open",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Open transport (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_start",
                action="handle_client_start",
                expected_state="active",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_START (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="nw_error",
                action="send_nw_error",
                expected_state="failed",
                expected_events=["session_failed"],
                evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
                description="Send NW_ERROR (identity CONFIRMED, effects SYNTHETIC)",
            ),
            ScenarioStep(
                step_id="nwrecover",
                action="send_nwrecover_notice",
                expected_state="failed",
                expected_events=["synthetic_disconnect"],
                evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
                description="Send NWRECOVER_NOTICE (identity CONFIRMED, effects SYNTHETIC)",
            ),
        ],
        evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
        source="G16 confirmed NWRECOVER_NOTICE identity, synthetic state effects",
        constraints="Recovery notice state effects are NOT confirmed",
    )


def _create_duplicate_start_rejection() -> ScenarioDefinition:
    """Create the duplicate start rejection scenario.

    Evidence: SYNTHETIC. Duplicate start rejection is confirmed by G16,
    but the specific error type is NOT confirmed.

    Note: The third step (duplicate start) will raise DuplicateStartError,
    which is caught by the harness and recorded as a failed step.
    This is the expected behavior - the scenario documents that duplicate
    start is rejected.
    """
    return ScenarioDefinition(
        scenario_id="duplicate_start_rejection",
        name="Duplicate Start Rejection",
        description=(
            "Session open, start, start again (rejected). "
            "Evidence: SYNTHETIC. Duplicate start rejection confirmed, "
            "but specific error type NOT confirmed."
        ),
        steps=[
            ScenarioStep(
                step_id="open",
                action="open",
                expected_state="transport_open",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Open transport (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="client_start",
                action="handle_client_start",
                expected_state="active",
                evidence_level=ScenarioEvidenceLevel.CONFIRMED,
                description="Handle CLIENT_START (CONFIRMED by G16)",
            ),
            ScenarioStep(
                step_id="duplicate_start",
                action="handle_client_start",
                expected_state="active",
                expected_events=[],
                evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
                description="Duplicate CLIENT_START (rejected, raises DuplicateStartError)",
            ),
        ],
        evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
        source="G16 confirmed duplicate start rejection",
        constraints="Specific error type NOT confirmed, step will fail in harness",
    )


def get_versioned_scenarios() -> list[ScenarioDefinition]:
    """Return all versioned synthetic scenarios.

    Returns:
        List of ScenarioDefinition instances.
    """
    return [
        _create_happy_path_lifecycle(),
        _create_error_path_cert_error(),
        _create_error_path_nw_error(),
        _create_recovery_path_nwrecover(),
        _create_duplicate_start_rejection(),
    ]


def get_scenario_version() -> str:
    """Return the scenario version.

    Returns:
        Version string.
    """
    return SCENARIO_VERSION
