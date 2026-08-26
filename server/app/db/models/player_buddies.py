"""Player buddy model."""

from sqlalchemy import Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerBuddy(Base):
    __tablename__ = "player_buddies"
    __table_args__ = (UniqueConstraint("player_id", "buddy_id", "buddy_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    buddy_id: Mapped[int] = mapped_column(Integer)
    buddy_key: Mapped[str] = mapped_column(String(35))
    buddy_value: Mapped[str] = mapped_column(String(35), server_default=text("'0'"))
