"""Battle service: manages active battle sessions.

STATUS: PROTOCOL_KNOWN - Implementation pending.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BattleService:
    """Stub battle service.

    TODO: Implement match creation, player assignment, result processing.
    """

    async def assign_match(self, match: dict[str, Any], game_mode: int) -> dict[str, Any]:
        """Handle RequestAssignMatch."""
        logger.info("assign_match: mode=%d (stub)", game_mode)
        return {"matchId": 0, "result": 0}

    async def enter_match(self, match_id: int, player_id: int) -> dict[str, Any]:
        """Handle RequestEnterMatch."""
        logger.info("enter_match: match=%d player=%d (stub)", match_id, player_id)
        return {"messageId": 0, "matchId": match_id, "playerId": player_id, "result": 0}

    async def intrude_match(self, match_id: int, player: dict[str, Any]) -> dict[str, Any]:
        """Handle RequestIntrudeMatch."""
        logger.info("intrude_match: match=%d (stub)", match_id)
        return {}
