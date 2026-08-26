"""Player weapon set model."""

from sqlalchemy import Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerWeaponSet(Base):
    __tablename__ = "player_weapon_set"
    __table_args__ = (UniqueConstraint("player_id", "weapon_set_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    weapon_set_id: Mapped[int] = mapped_column(Integer)
    use_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    use_time: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
