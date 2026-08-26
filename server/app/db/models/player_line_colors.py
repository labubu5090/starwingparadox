"""Player line color model."""

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerLineColor(Base):
    __tablename__ = "player_line_colors"
    __table_args__ = (UniqueConstraint("player_id", "line_color_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    line_color_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer, default=0)
