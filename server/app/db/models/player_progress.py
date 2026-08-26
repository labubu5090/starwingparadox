"""Player progress model."""

from sqlalchemy import Integer, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerProgress(Base):
    __tablename__ = "player_progress"
    __table_args__ = (UniqueConstraint("player_id", "progress_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    progress_key: Mapped[str] = mapped_column(String(35))
    status: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
