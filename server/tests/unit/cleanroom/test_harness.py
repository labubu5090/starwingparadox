"""Tests for session scenario harness (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.harness import (
    ScenarioDefinition,
    ScenarioEvidenceLevel,
    ScenarioHarness,
    ScenarioResult,
    ScenarioStep,
)


class TestScenarioStep:
    """Test scenario step."""

    def test_step_creation(self):
        step = ScenarioStep(
            step_id="test",
            action="open",
            expected_state="transport_open",
            evidence_level=ScenarioEvidenceLevel.CONFIRMED,
        )
        assert step.step_id == "test"
        assert step.action == "open"
        assert step.expected_state == "transport_open"
        assert step.evidence_level == ScenarioEvidenceLevel.CONFIRMED

    def test_step_frozen(self):
        step = ScenarioStep(
            step_id="test",
            action="open",
        )
        with pytest.raises(AttributeError):
            step.step_id = "changed"


class TestScenarioDefinition:
    """Test scenario definition."""

    def test_definition_creation(self):
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test Scenario",
            description="Test description",
            steps=[],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test source",
        )
        assert scenario.scenario_id == "test"
        assert scenario.name == "Test Scenario"
        assert scenario.description == "Test description"
        assert scenario.steps == []
        assert scenario.evidence_level == ScenarioEvidenceLevel.SYNTHETIC

    def test_definition_frozen(self):
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        with pytest.raises(AttributeError):
            scenario.scenario_id = "changed"


class TestScenarioResult:
    """Test scenario result."""

    def test_result_creation(self):
        result = ScenarioResult(
            step_id="test",
            success=True,
            actual_state="transport_open",
            actual_events=["transport_opened"],
        )
        assert result.step_id == "test"
        assert result.success is True
        assert result.actual_state == "transport_open"
        assert result.actual_events == ["transport_opened"]
        assert result.error is None

    def test_result_with_error(self):
        result = ScenarioResult(
            step_id="test",
            success=False,
            actual_state="failed",
            actual_events=[],
            error="Test error",
        )
        assert result.error == "Test error"


class TestScenarioHarness:
    """Test scenario harness."""

    @pytest.mark.asyncio
    async def test_register_scenario(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        assert harness.get_scenario("test") is not None

    @pytest.mark.asyncio
    async def test_register_duplicate_raises(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        with pytest.raises(ValueError):
            harness.register_scenario(scenario)

    @pytest.mark.asyncio
    async def test_get_scenario_not_found(self):
        harness = ScenarioHarness()
        assert harness.get_scenario("nonexistent") is None

    @pytest.mark.asyncio
    async def test_get_all_scenarios(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        assert len(harness.get_all_scenarios()) == 1

    @pytest.mark.asyncio
    async def test_run_scenario_not_found(self):
        harness = ScenarioHarness()
        with pytest.raises(KeyError):
            await harness.run_scenario("nonexistent")

    @pytest.mark.asyncio
    async def test_run_happy_path(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="happy_path",
            name="Happy Path",
            description="Test happy path",
            steps=[
                ScenarioStep(
                    step_id="open",
                    action="open",
                    expected_state="transport_open",
                ),
                ScenarioStep(
                    step_id="client_start",
                    action="handle_client_start",
                    expected_state="active",
                ),
                ScenarioStep(
                    step_id="client_end",
                    action="handle_client_end",
                    expected_state="closed",
                ),
            ],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        results = await harness.run_scenario("happy_path")
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_run_error_path(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="error_path",
            name="Error Path",
            description="Test error path",
            steps=[
                ScenarioStep(
                    step_id="open",
                    action="open",
                    expected_state="transport_open",
                ),
                ScenarioStep(
                    step_id="client_start",
                    action="handle_client_start",
                    expected_state="active",
                ),
                ScenarioStep(
                    step_id="cert_error",
                    action="send_cert_error",
                    expected_state="failed",
                ),
            ],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        results = await harness.run_scenario("error_path")
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_unknown_action_fails(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="unknown_action",
            name="Unknown Action",
            description="Test unknown action",
            steps=[
                ScenarioStep(
                    step_id="unknown",
                    action="unknown_action",
                ),
            ],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        results = await harness.run_scenario("unknown_action")
        assert len(results) == 1
        assert not results[0].success
        assert "Unknown action" in results[0].error

    @pytest.mark.asyncio
    async def test_get_results(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[
                ScenarioStep(
                    step_id="open",
                    action="open",
                    expected_state="transport_open",
                ),
            ],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        await harness.run_scenario("test")
        assert len(harness.get_results()) == 1

    @pytest.mark.asyncio
    async def test_clear_results(self):
        harness = ScenarioHarness()
        scenario = ScenarioDefinition(
            scenario_id="test",
            name="Test",
            description="Test",
            steps=[
                ScenarioStep(
                    step_id="open",
                    action="open",
                    expected_state="transport_open",
                ),
            ],
            evidence_level=ScenarioEvidenceLevel.SYNTHETIC,
            source="test",
        )
        harness.register_scenario(scenario)
        await harness.run_scenario("test")
        harness.clear_results()
        assert len(harness.get_results()) == 0
