"""Player model."""

from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Player(Base):
    __tablename__ = "player"

    player_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nesys_id: Mapped[str] = mapped_column(String(22))
    player_name: Mapped[str] = mapped_column(String(50), default="ＮｏＮａｍｅ")
    rank_id: Mapped[int] = mapped_column(Integer, default=0)
    rank_id_2on2: Mapped[int] = mapped_column(Integer, default=0)
    title_id: Mapped[int] = mapped_column(Integer, default=0)
    title_id_2on2: Mapped[int] = mapped_column(Integer, default=0)
    buddy_id: Mapped[int] = mapped_column(SmallInteger, default=0)
    buddy_intimacy: Mapped[int] = mapped_column(SmallInteger, default=0)
    line_color_id: Mapped[int] = mapped_column(Integer, default=0)
    ranking_pref_name: Mapped[str] = mapped_column(String(30), default="東京")
    last_ranking_pref_name: Mapped[str] = mapped_column(String(30), default="東京")
    match_mode_id: Mapped[int] = mapped_column(Integer, default=0)
    violation_point: Mapped[int] = mapped_column(Integer, default=0)
    emblem_id: Mapped[int] = mapped_column(Integer, default=0)
    line_color_id_2on2: Mapped[int] = mapped_column(Integer, default=0)
    emblem_id_2on2: Mapped[int] = mapped_column(Integer, default=0)
    birth_day: Mapped[int] = mapped_column(Integer, default=1)
    birth_month: Mapped[int] = mapped_column(Integer, default=1)
    mecha_set_id: Mapped[int] = mapped_column(Integer, default=0)
    side_weapon_id: Mapped[int] = mapped_column(Integer, default=0)
    mecha_preset_id: Mapped[int] = mapped_column(Integer, default=0)
    rank_point: Mapped[int] = mapped_column(Integer, default=0)
    max_rank_id: Mapped[int] = mapped_column(Integer, default=0)
    rank_point_2on2: Mapped[int] = mapped_column(Integer, default=0)
    max_rank_id_2on2: Mapped[int] = mapped_column(Integer, default=0)
