"""Player mecha set part model."""

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerMechaSetPart(Base):
    __tablename__ = "player_mecha_set_parts"
    __table_args__ = (UniqueConstraint("player_id", "mecha_set_id", "part_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    mecha_set_id: Mapped[int] = mapped_column(Integer)
    part_id: Mapped[int] = mapped_column(Integer)
    mecha_id: Mapped[int] = mapped_column(Integer)
    design_id: Mapped[int] = mapped_column(Integer, default=0)
    color_id: Mapped[int] = mapped_column(Integer, default=0)
