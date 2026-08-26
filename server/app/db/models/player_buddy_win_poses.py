"""Player buddy win pose model."""

from sqlalchemy import Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerBuddyWinPose(Base):
    __tablename__ = "player_buddy_win_poses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    buddy_id: Mapped[int] = mapped_column(Integer)
    win_pose_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
