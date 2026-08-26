"""Player weapon set slot model."""

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerWeaponSetSlot(Base):
    __tablename__ = "player_weapon_set_slots"
    __table_args__ = (UniqueConstraint("player_id", "weapon_set_id", "slot_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    weapon_set_id: Mapped[int] = mapped_column(Integer)
    slot_id: Mapped[int] = mapped_column(Integer)
    weapon_id: Mapped[int] = mapped_column(Integer)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    use_time: Mapped[int] = mapped_column(Integer, default=0)
