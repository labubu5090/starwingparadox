"""Player title model."""

from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerTitle(Base):
    __tablename__ = "player_titles"
    __table_args__ = (UniqueConstraint("player_id", "title_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    title_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer, default=0)
