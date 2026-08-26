"""Player option model."""

from sqlalchemy import Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerOption(Base):
    __tablename__ = "player_options"
    __table_args__ = (UniqueConstraint("player_id", "option_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    option_key: Mapped[str] = mapped_column(String(35))
    value_num: Mapped[int] = mapped_column(Integer, server_default=text("0"))
