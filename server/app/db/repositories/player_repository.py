"""Player repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.player import Player


class PlayerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_player_id(self, player_id: int) -> Player | None:
        result = await self.session.execute(select(Player).where(Player.player_id == player_id))
        return result.scalar_one_or_none()

    async def get_by_nesys_id(self, nesys_id: str) -> Player | None:
        result = await self.session.execute(select(Player).where(Player.nesys_id == nesys_id))
        return result.scalar_one_or_none()

    async def create_player(self, nesys_id: str) -> Player:
        player = Player(nesys_id=nesys_id)
        self.session.add(player)
        await self.session.flush()
        await self.session.refresh(player)
        return player

    async def update_player(self, player_id: int, **kwargs: object) -> Player | None:
        player = await self.get_by_player_id(player_id)
        if player is None:
            return None
        for key, value in kwargs.items():
            if hasattr(player, key):
                setattr(player, key, value)
        await self.session.flush()
        await self.session.refresh(player)
        return player
