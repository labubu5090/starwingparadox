"""Player service: business logic layer for player operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.player_repository import PlayerRepository

logger = logging.getLogger(__name__)


class PlayerService:
    """Wraps repository calls and implements player business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = PlayerRepository(db)

    async def load_profile_by_nesys(self, nesys_id: str) -> dict[str, Any]:
        """Load a player profile by NESYS ID."""
        player = await self.repo.get_by_nesys_id(nesys_id)
        if player is None:
            return {}
        return {
            "playerId": player.player_id,
            "nesysId": player.nesys_id,
            "playerName": player.player_name,
            "playerRank": player.rank_id,
        }

    async def login_player(
        self, player_id: int, ip_addr: str, request_body: dict[str, Any]
    ) -> dict[str, Any]:
        """Authenticate and return player data for login."""
        player = await self.repo.get_by_player_id(player_id)
        if player is None:
            return {"result": 1, "message": "Player not found"}
        return {
            "result": 0,
            "playerId": player.player_id,
            "playerName": player.player_name,
            "playerRank": player.rank_id,
        }

    async def register_player(self, player_id: int, request_body: dict[str, Any]) -> dict[str, Any]:
        """Register a new player."""
        existing = await self.repo.get_by_player_id(player_id)
        if existing is not None:
            return {"result": 1, "message": "Player already exists"}
        await self.repo.create_player(
            nesys_id=request_body.get("nesysId", ""),
        )
        return {"result": 0, "message": "Registered"}

    async def load_game_data(self, player_id: int) -> dict[str, Any]:
        """Load full game data for a player."""
        player = await self.repo.get_by_player_id(player_id)
        if player is None:
            return {}
        return {
            "playerId": player.player_id,
        }

    async def load_game_data_missions(self, player_id: int) -> dict[str, Any]:
        """Load mission-specific game data for a player."""
        player = await self.repo.get_by_player_id(player_id)
        if player is None:
            return {}
        return {
            "playerId": player.player_id,
        }

    async def save_game_data(self, player_id: int, request_body: dict[str, Any]) -> dict[str, Any]:
        """Save game data for a player."""
        player = await self.repo.get_by_player_id(player_id)
        if player is None:
            return {"result": 1, "message": "Player not found"}
        return {"result": 0, "message": "Saved"}
