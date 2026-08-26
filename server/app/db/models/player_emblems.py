"""Player emblem model."""

from sqlalchemy import Boolean, Integer, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlayerEmblem(Base):
    __tablename__ = "player_emblems"
    __table_args__ = (UniqueConstraint("player_id", "emblem_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(Integer)
    emblem_id: Mapped[int] = mapped_column(Integer)

    outline_part_id: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    outline_offset_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    outline_offset_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    outline_scale_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    outline_scale_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    outline_angle: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    main_design_part_id: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    main_design_offset_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    main_design_offset_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    main_design_scale_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    main_design_scale_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    main_design_angle: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    sub_design_part_id: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sub_design_offset_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sub_design_offset_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sub_design_scale_x: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sub_design_scale_y: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    sub_design_angle: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    status: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    editable: Mapped[bool] = mapped_column(Boolean, server_default=text("0"))
