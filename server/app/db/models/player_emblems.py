"""Player emblem model."""

from sqlalchemy import Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerEmblem(Base):
    __tablename__ = "player_emblems"
    __table_args__ = (UniqueConstraint("player_id", "emblem_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    emblem_id: Mapped[int] = mapped_column(Integer)

    outline_type: Mapped[int] = mapped_column(Integer, default=0)
    outline_color_r: Mapped[int] = mapped_column(Integer, default=0)
    outline_color_g: Mapped[int] = mapped_column(Integer, default=0)
    outline_color_b: Mapped[int] = mapped_column(Integer, default=0)
    outline_color_a: Mapped[int] = mapped_column(Integer, default=0)
    outline_size: Mapped[int] = mapped_column(Integer, default=0)
    outline_rot: Mapped[int] = mapped_column(Integer, default=0)
    outline_pos_x: Mapped[int] = mapped_column(Integer, default=0)
    outline_pos_y: Mapped[int] = mapped_column(Integer, default=0)

    main_design_type: Mapped[int] = mapped_column(Integer, default=0)
    main_design_color_r: Mapped[int] = mapped_column(Integer, default=0)
    main_design_color_g: Mapped[int] = mapped_column(Integer, default=0)
    main_design_color_b: Mapped[int] = mapped_column(Integer, default=0)
    main_design_color_a: Mapped[int] = mapped_column(Integer, default=0)
    main_design_size: Mapped[int] = mapped_column(Integer, default=0)
    main_design_rot: Mapped[int] = mapped_column(Integer, default=0)
    main_design_pos_x: Mapped[int] = mapped_column(Integer, default=0)
    main_design_pos_y: Mapped[int] = mapped_column(Integer, default=0)

    sub_design_type: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_color_r: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_color_g: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_color_b: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_color_a: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_size: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_rot: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_pos_x: Mapped[int] = mapped_column(Integer, default=0)
    sub_design_pos_y: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[int] = mapped_column(Integer, default=0)
    editable: Mapped[bool] = mapped_column(Boolean, default=False)
