"""Player emblem part model."""

from sqlalchemy import Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerEmblemPart(Base):
    __tablename__ = "player_emblem_parts"
    __table_args__ = (UniqueConstraint("player_id", "part_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    part_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
