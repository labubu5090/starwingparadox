"""Player side weapon model."""

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerSideWeapon(Base):
    __tablename__ = "player_side_weapons"
    __table_args__ = (UniqueConstraint("player_id", "side_weapon_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    side_weapon_id: Mapped[int] = mapped_column(Integer)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    use_time: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0)
