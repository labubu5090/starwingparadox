"""Player mecha color model."""

from sqlalchemy import Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerMechaColor(Base):
    __tablename__ = "player_mecha_colors"
    __table_args__ = (UniqueConstraint("player_id", "mecha_color_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    mecha_color_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
