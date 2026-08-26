"""Player mecha set model."""

from sqlalchemy import Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerMechaSet(Base):
    __tablename__ = "player_mecha_sets"
    __table_args__ = (UniqueConstraint("player_id", "mecha_set_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    mecha_set_id: Mapped[int] = mapped_column(Integer)
    mecha_setbonus_id: Mapped[int] = mapped_column(Integer)
    weapon_set_id: Mapped[int] = mapped_column(Integer)
    is_decal: Mapped[bool] = mapped_column(Boolean, default=False)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    use_time: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=0)
    win_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    winning_streaks: Mapped[int | None] = mapped_column(Integer, nullable=True)
