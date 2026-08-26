"""Player login model."""

from sqlalchemy import DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerLogin(Base):
    __tablename__ = "player_logins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    ip_addr: Mapped[str] = mapped_column(String)
    location_id: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    client_version: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    data_version: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    ts_when: Mapped[str | None] = mapped_column(DateTime, nullable=True)
