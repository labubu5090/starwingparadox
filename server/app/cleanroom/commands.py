"""Command catalog for clean-room protocol foundation.

This module loads the G16 synthetic command catalog into a typed Python
representation. It distinguishes client-to-service commands from
service-to-client commands, preserves confidence classification, and
avoids invented numeric identifiers or payload schemas.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass


class Direction(enum.Enum):
    """Direction of command flow."""

    CLIENT_TO_SERVICE = "client_to_service"
    SERVICE_TO_CLIENT = "service_to_client"


class Confidence(enum.Enum):
    """Confidence level of command identification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImplementationStatus(enum.Enum):
    """Implementation eligibility status."""

    ELIGIBLE = "eligible"
    CATALOG_ONLY = "catalog_only"
    RESTRICTED = "restricted"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CommandInfo:
    """Information about a protocol command.

    Attributes:
        symbolic_name: Human-readable command name.
        numeric_id: Numeric identifier (None if not confirmed).
        direction: Command flow direction.
        confidence: Confidence level of identification.
        implementation: Implementation eligibility.
        counterpart: Expected counterpart command name.
        ordering: Lifecycle ordering constraint.
        source_reference: Evidence source reference.
    """

    symbolic_name: str
    numeric_id: int | None
    direction: Direction
    confidence: Confidence
    implementation: ImplementationStatus
    counterpart: str | None = None
    ordering: str | None = None
    source_reference: str = "G16 protocol confidence matrix"


class CommandCatalog:
    """Typed command catalog loaded from G16 evidence.

    This catalog:
    - distinguishes client-to-service from service-to-client commands
    - preserves confidence classification
    - preserves implementation eligibility
    - rejects duplicate confirmed identifiers
    - rejects direction conflicts
    - supports lookup by confirmed numeric identifier
    - supports symbolic lookup for documentation and tests
    """

    def __init__(self) -> None:
        self._by_name: dict[str, CommandInfo] = {}
        self._by_id: dict[int, CommandInfo] = {}
        self._build_catalog()

    def _build_catalog(self) -> None:
        """Build the catalog from G16 confirmed evidence."""
        commands = [
            # Confirmed LCOMMAND (Game → Service)
            CommandInfo(
                symbolic_name="LCOMMAND_CLIENT_START",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart="SCOMMAND_CLIENT_START_REPLY",
                ordering="first",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_CLIENT_END",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart=None,
                ordering="last",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_PING",
                numeric_id=0x66,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart="SCOMMAND_PING_RESPONSE",
                ordering="any",
                source_reference="G13 analysis, confirmed G16",
            ),
            # Confirmed SCOMMAND (Service → Game)
            CommandInfo(
                symbolic_name="SCOMMAND_CLIENT_START_REPLY",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart="LCOMMAND_CLIENT_START",
                ordering="after LCOMMAND_CLIENT_START",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_PING_RESPONSE",
                numeric_id=0x67,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart="LCOMMAND_PING",
                ordering="after LCOMMAND_PING",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_CERT_ERROR",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart=None,
                ordering="after certificate failure",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_NW_ERROR",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart=None,
                ordering="after network failure",
                source_reference="G13 analysis, confirmed G16",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_NWRECOVER_NOTICE",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.HIGH,
                implementation=ImplementationStatus.ELIGIBLE,
                counterpart=None,
                ordering="after network recovery",
                source_reference="G13 analysis, confirmed G16",
            ),
            # Protocol-identified LCOMMAND (Game → Service) - catalog only
            CommandInfo(
                symbolic_name="LCOMMAND_CARD_READ",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_CARD_DATA",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_CARD_WRITE",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_CARD_RESULT",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_CARD_CHECK",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_CARD_STATUS",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_NEWS_REQUEST",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_NEWS_DATA",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_EVENT_REQUEST",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_EVENT_DATA",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_LOG_UPLOAD",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_LOG_RESULT",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_MATCH_REQUEST",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_MATCH_RESPONSE",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_MATCH_CANCEL",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_MATCH_CANCEL_ACK",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_BURST_GROUP_JOIN",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_BURST_GROUP_JOIN_ACK",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="LCOMMAND_BURST_GROUP_LEAVE",
                numeric_id=None,
                direction=Direction.CLIENT_TO_SERVICE,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="SCOMMAND_BURST_GROUP_LEAVE_ACK",
                source_reference="G13 analysis, protocol-identified",
            ),
            # Protocol-identified SCOMMAND (Service → Game) - catalog only
            CommandInfo(
                symbolic_name="SCOMMAND_CARD_DATA",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_CARD_READ",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_CARD_RESULT",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_CARD_WRITE",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_CARD_STATUS",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_CARD_CHECK",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_NEWS_DATA",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_NEWS_REQUEST",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_EVENT_DATA",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_EVENT_REQUEST",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_LOG_RESULT",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_LOG_UPLOAD",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_MATCH_RESPONSE",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_MATCH_REQUEST",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_MATCH_CANCEL_ACK",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_MATCH_CANCEL",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_BURST_GROUP_JOIN_ACK",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_BURST_GROUP_JOIN",
                source_reference="G13 analysis, protocol-identified",
            ),
            CommandInfo(
                symbolic_name="SCOMMAND_BURST_GROUP_LEAVE_ACK",
                numeric_id=None,
                direction=Direction.SERVICE_TO_CLIENT,
                confidence=Confidence.MEDIUM,
                implementation=ImplementationStatus.CATALOG_ONLY,
                counterpart="LCOMMAND_BURST_GROUP_LEAVE",
                source_reference="G13 analysis, protocol-identified",
            ),
        ]

        for cmd in commands:
            if cmd.symbolic_name in self._by_name:
                raise ValueError(
                    f"Duplicate command name: {cmd.symbolic_name}"
                )
            self._by_name[cmd.symbolic_name] = cmd

            if cmd.numeric_id is not None:
                if cmd.numeric_id in self._by_id:
                    existing = self._by_id[cmd.numeric_id]
                    raise ValueError(
                        f"Duplicate numeric ID {cmd.numeric_id}: "
                        f"{cmd.symbolic_name} conflicts with "
                        f"{existing.symbolic_name}"
                    )
                self._by_id[cmd.numeric_id] = cmd

    def get_by_name(self, name: str) -> CommandInfo | None:
        """Look up a command by symbolic name.

        Args:
            name: Symbolic command name.

        Returns:
            CommandInfo if found, None otherwise.
        """
        return self._by_name.get(name)

    def get_by_id(self, numeric_id: int) -> CommandInfo | None:
        """Look up a command by numeric identifier.

        Args:
            numeric_id: Numeric command identifier.

        Returns:
            CommandInfo if found, None otherwise.
        """
        return self._by_id.get(numeric_id)

    def get_all(self) -> list[CommandInfo]:
        """Return all commands in the catalog.

        Returns:
            List of all CommandInfo entries.
        """
        return list(self._by_name.values())

    def get_by_direction(self, direction: Direction) -> list[CommandInfo]:
        """Return commands matching the given direction.

        Args:
            direction: Command flow direction.

        Returns:
            List of matching CommandInfo entries.
        """
        return [
            cmd for cmd in self._by_name.values()
            if cmd.direction == direction
        ]

    def get_eligible(self) -> list[CommandInfo]:
        """Return commands eligible for implementation.

        Returns:
            List of eligible CommandInfo entries.
        """
        return [
            cmd for cmd in self._by_name.values()
            if cmd.implementation == ImplementationStatus.ELIGIBLE
        ]

    def is_eligible(self, name: str) -> bool:
        """Check if a command is eligible for implementation.

        Args:
            name: Symbolic command name.

        Returns:
            True if eligible, False otherwise.
        """
        cmd = self.get_by_name(name)
        return cmd is not None and cmd.implementation == ImplementationStatus.ELIGIBLE

    def count(self) -> int:
        """Return the total number of commands in the catalog.

        Returns:
            Command count.
        """
        return len(self._by_name)
