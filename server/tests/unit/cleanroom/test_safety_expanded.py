"""Tests for expanded safety guards (G18)."""
from __future__ import annotations

import pytest

from app.cleanroom.safety import (
    GuardLevel,
    GuardResult,
    SafetyGuardChecker,
)


class TestGuardLevel:
    """Test guard level."""

    def test_guard_levels_exist(self):
        assert GuardLevel.CONFIRMED.value == "confirmed"
        assert GuardLevel.SYNTHETIC.value == "synthetic"
        assert GuardLevel.UNKNOWN.value == "unknown"

    def test_guard_level_count(self):
        assert len(GuardLevel) == 3


class TestGuardResult:
    """Test guard result."""

    def test_result_creation(self):
        result = GuardResult(
            name="test",
            passed=True,
            level=GuardLevel.CONFIRMED,
            details="test details",
        )
        assert result.name == "test"
        assert result.passed is True
        assert result.level == GuardLevel.CONFIRMED
        assert result.details == "test details"

    def test_result_frozen(self):
        result = GuardResult(
            name="test",
            passed=True,
            level=GuardLevel.CONFIRMED,
        )
        with pytest.raises(AttributeError):
            result.passed = False


class TestSafetyGuardChecker:
    """Test safety guard checker."""

    def test_check_cleanroom_dir(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        results = checker.check_all_guards()
        assert len(results) == 5
        assert all(r.passed for r in results)

    def test_check_no_prohibited_imports(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        result = checker.check_no_prohibited_imports()
        assert result.passed
        assert result.level == GuardLevel.CONFIRMED

    def test_check_no_production_hostnames(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        result = checker.check_no_production_hostnames()
        assert result.passed
        assert result.level == GuardLevel.CONFIRMED

    def test_check_no_pipe_paths(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        result = checker.check_no_pipe_paths()
        assert result.passed
        assert result.level == GuardLevel.CONFIRMED

    def test_check_no_certificate_references(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        result = checker.check_no_certificate_references()
        assert result.passed
        assert result.level == GuardLevel.CONFIRMED

    def test_check_no_registry_paths(self):
        checker = SafetyGuardChecker("C:\\Users\\KAHO\\Pictures\\Starwing\\server\\app\\cleanroom")
        result = checker.check_no_registry_paths()
        assert result.passed
        assert result.level == GuardLevel.CONFIRMED
