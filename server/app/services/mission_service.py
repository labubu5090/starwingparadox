"""Mission service: handles mission/co-op game mode logic.

STATUS: PROTOCOL_KNOWN - Implementation pending.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MissionService:
    """Stub mission service.

    TODO: Implement mission progression, co-op mode management.
    """

    async def load_missions(self, player_id: int) -> dict[str, Any]:
        """Load mission data for a player."""
        logger.info("load_missions: player=%d (stub)", player_id)
        return {"playerId": player_id, "missions": []}

    async def update_mission(self, player_id: int, mission_data: dict[str, Any]) -> dict[str, Any]:
        """Update mission progress."""
        logger.info("update_mission: player=%d (stub)", player_id)
        return {"result": 0}
