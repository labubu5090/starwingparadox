"""Player mission model."""

from sqlalchemy import Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerMission(Base):
    __tablename__ = "player_missions"
    __table_args__ = (UniqueConstraint("player_id", "mission_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    mission_id: Mapped[int] = mapped_column(Integer)
    clear_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    clear_num: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    mission_status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
