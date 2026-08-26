"""Matching service: orchestrates matchmaking flows.

STATUS: PROTOCOL_KNOWN - Implementation pending.
Matching protocol messages are defined in starwingMessage.proto.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MatchingService:
    """Stub matching service.

    TODO: Implement matching queue, burst group management, and match lifecycle.
    """

    async def entry_matching(self, player_id: int, request: dict[str, Any]) -> dict[str, Any]:
        """Handle RequestEntryMatching (messageType=200)."""
        logger.info("entry_matching: player=%d (stub)", player_id)
        return {"messageType": 201, "messageId": 0, "timeout": 30}

    async def cancel_matching(self, player_id: int, match_id: int) -> dict[str, Any]:
        """Handle RequestCancelMatching (messageType=202)."""
        logger.info("cancel_matching: player=%d match=%d (stub)", player_id, match_id)
        return {"messageType": 0xCC, "matchId": match_id, "playerId": player_id}

    async def join_matching(self, player_id: int, match_id: int) -> dict[str, Any]:
        """Handle RequestJoinMatching (messageType=206)."""
        logger.info("join_matching: player=%d match=%d (stub)", player_id, match_id)
        return {}

    async def entry_burst_group(self, player_id: int, request: dict[str, Any]) -> dict[str, Any]:
        """Handle RequestEntryBurstGroup (messageType=208)."""
        logger.info("entry_burst_group: player=%d (stub)", player_id)
        return {"messageType": 209, "messageId": 0, "timeout": 30, "burstNumMax": 4}

    async def change_burst_group_mode(
        self, player_id: int, request: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle RequestChangeBurstGroupMode (messageType=210)."""
        logger.info("change_burst_group_mode: player=%d (stub)", player_id)
        return {"messageType": 211, "messageId": 0, "result": 0, "player": []}

    async def update_burst_group(self, player_id: int) -> dict[str, Any]:
        """Handle RequestUpdateBurstGroup (messageType=214)."""
        logger.info("update_burst_group: player=%d (stub)", player_id)
        return {"messageType": 215, "player": []}

    async def burst_group_select(self, player_id: int, request: dict[str, Any]) -> dict[str, Any]:
        """Handle RequestBurstGroupSelect (messageType=216)."""
        logger.info("burst_group_select: player=%d (stub)", player_id)
        return {"messageType": 217, "messageId": 0, "result": 0, "timeout": 30}
