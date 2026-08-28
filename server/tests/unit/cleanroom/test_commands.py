"""Tests for command catalog."""
from __future__ import annotations

from app.cleanroom.commands import (
    CommandCatalog,
    Confidence,
    Direction,
    ImplementationStatus,
)


class TestCommandCatalogInit:
    """Test catalog initialization."""

    def test_catalog_loads_all_commands(self):
        catalog = CommandCatalog()
        assert catalog.count() == 28

    def test_catalog_has_confirmed_lcommand(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("LCOMMAND_PING")
        assert cmd is not None
        assert cmd.numeric_id == 0x66
        assert cmd.direction == Direction.CLIENT_TO_SERVICE
        assert cmd.confidence == Confidence.HIGH
        assert cmd.implementation == ImplementationStatus.ELIGIBLE

    def test_catalog_has_confirmed_scommand(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("SCOMMAND_PING_RESPONSE")
        assert cmd is not None
        assert cmd.numeric_id == 0x67
        assert cmd.direction == Direction.SERVICE_TO_CLIENT
        assert cmd.confidence == Confidence.HIGH
        assert cmd.implementation == ImplementationStatus.ELIGIBLE


class TestCommandCatalogLookup:
    """Test catalog lookup methods."""

    def test_get_by_name_existing(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("LCOMMAND_CLIENT_START")
        assert cmd is not None
        assert cmd.symbolic_name == "LCOMMAND_CLIENT_START"

    def test_get_by_name_nonexisting(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("NONEXISTENT")
        assert cmd is None

    def test_get_by_id_existing(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_id(0x66)
        assert cmd is not None
        assert cmd.symbolic_name == "LCOMMAND_PING"

    def test_get_by_id_nonexisting(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_id(999)
        assert cmd is None

    def test_get_by_id_no_id_command(self):
        catalog = CommandCatalog()
        # CLIENT_START has no numeric ID
        cmd = catalog.get_by_name("LCOMMAND_CLIENT_START")
        assert cmd is not None
        assert cmd.numeric_id is None


class TestCommandCatalogDirection:
    """Test catalog direction filtering."""

    def test_get_client_to_service(self):
        catalog = CommandCatalog()
        cmds = catalog.get_by_direction(Direction.CLIENT_TO_SERVICE)
        assert len(cmds) == 13  # 3 confirmed + 10 protocol-identified

    def test_get_service_to_client(self):
        catalog = CommandCatalog()
        cmds = catalog.get_by_direction(Direction.SERVICE_TO_CLIENT)
        assert len(cmds) == 15  # 5 confirmed + 10 protocol-identified

    def test_direction_counts_match(self):
        catalog = CommandCatalog()
        c2s = catalog.get_by_direction(Direction.CLIENT_TO_SERVICE)
        s2c = catalog.get_by_direction(Direction.SERVICE_TO_CLIENT)
        assert len(c2s) + len(s2c) == catalog.count()


class TestCommandCatalogEligibility:
    """Test catalog eligibility filtering."""

    def test_get_eligible(self):
        catalog = CommandCatalog()
        eligible = catalog.get_eligible()
        assert len(eligible) == 8  # 3 LCOMMAND + 5 SCOMMAND confirmed

    def test_is_eligible_confirmed(self):
        catalog = CommandCatalog()
        assert catalog.is_eligible("LCOMMAND_PING") is True
        assert catalog.is_eligible("SCOMMAND_PING_RESPONSE") is True

    def test_is_eligible_catalog_only(self):
        catalog = CommandCatalog()
        assert catalog.is_eligible("LCOMMAND_CARD_READ") is False

    def test_is_eligible_nonexistent(self):
        catalog = CommandCatalog()
        assert catalog.is_eligible("NONEXISTENT") is False


class TestCommandCatalogAll:
    """Test get_all method."""

    def test_get_all_returns_all_commands(self):
        catalog = CommandCatalog()
        all_cmds = catalog.get_all()
        assert len(all_cmds) == catalog.count()

    def test_get_all_returns_copy(self):
        catalog = CommandCatalog()
        all_cmds = catalog.get_all()
        all_cmds.clear()
        assert catalog.count() == 28


class TestCommandCatalogCounterparts:
    """Test command counterpart relationships."""

    def test_client_start_counterpart(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("LCOMMAND_CLIENT_START")
        assert cmd is not None
        assert cmd.counterpart == "SCOMMAND_CLIENT_START_REPLY"

    def test_ping_counterpart(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("LCOMMAND_PING")
        assert cmd is not None
        assert cmd.counterpart == "SCOMMAND_PING_RESPONSE"

    def test_card_read_counterpart(self):
        catalog = CommandCatalog()
        cmd = catalog.get_by_name("LCOMMAND_CARD_READ")
        assert cmd is not None
        assert cmd.counterpart == "SCOMMAND_CARD_DATA"
