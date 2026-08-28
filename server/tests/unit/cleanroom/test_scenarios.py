"""Tests for versioned synthetic scenarios (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.harness import ScenarioHarness
from app.cleanroom.scenarios import (
    SCENARIO_VERSION,
    get_scenario_version,
    get_versioned_scenarios,
)


class TestScenarioVersion:
    """Test scenario version."""

    def test_version_format(self):
        version = get_scenario_version()
        assert version == SCENARIO_VERSION
        parts = version.split(".")
        assert len(parts) == 3

    def test_version_constant(self):
        assert SCENARIO_VERSION == "1.0.0"


class TestVersionedScenarios:
    """Test versioned scenarios."""

    def test_scenarios_count(self):
        scenarios = get_versioned_scenarios()
        assert len(scenarios) == 5

    def test_scenario_ids_unique(self):
        scenarios = get_versioned_scenarios()
        ids = [s.scenario_id for s in scenarios]
        assert len(ids) == len(set(ids))

    def test_scenario_has_steps(self):
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            assert len(scenario.steps) > 0

    def test_scenario_evidence_levels(self):
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            assert scenario.evidence_level is not None
            for step in scenario.steps:
                assert step.evidence_level is not None

    @pytest.mark.asyncio
    async def test_happy_path_runs(self):
        harness = ScenarioHarness()
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            harness.register_scenario(scenario)

        results = await harness.run_scenario("happy_path_lifecycle")
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_cert_error_path_runs(self):
        harness = ScenarioHarness()
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            harness.register_scenario(scenario)

        results = await harness.run_scenario("error_path_cert_error")
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_nw_error_path_runs(self):
        harness = ScenarioHarness()
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            harness.register_scenario(scenario)

        results = await harness.run_scenario("error_path_nw_error")
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_nwrecover_path_runs(self):
        harness = ScenarioHarness()
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            harness.register_scenario(scenario)

        results = await harness.run_scenario("recovery_path_nwrecover")
        assert len(results) == 4
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_duplicate_start_runs(self):
        harness = ScenarioHarness()
        scenarios = get_versioned_scenarios()
        for scenario in scenarios:
            harness.register_scenario(scenario)

        results = await harness.run_scenario("duplicate_start_rejection")
        assert len(results) == 3
        # First two steps succeed, third step fails (DuplicateStartError)
        assert results[0].success
        assert results[1].success
        assert not results[2].success
