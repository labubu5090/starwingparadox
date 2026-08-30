"""Local profile model for private server operator-owned profiles."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class LocalProfile(Base):
    """Operator-owned local profile.

    This profile is entirely private-server-owned and has no relationship
    to NESYS authentication, NESiCA identity, vendor certificates,
    production matching, production entitlement, or payment systems.
    """

    __tablename__ = "local_profile"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=_new_uuid
    )
    display_name: Mapped[str] = mapped_column(String(32), nullable=False, default="Player")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Tutorial tracking (local only, no NESYS dependency)
    tutorial_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tutorial_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    tutorial_last_result: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Local settings
    preferred_controller_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    settings_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Session tracking
    session_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    session_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Operator notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "profile_uuid": self.profile_uuid,
            "display_name": self.display_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "tutorial_attempts": self.tutorial_attempts,
            "tutorial_completed": self.tutorial_completed,
            "tutorial_last_result": self.tutorial_last_result,
            "preferred_controller_index": self.preferred_controller_index,
            "settings_json": self.settings_json,
            "session_active": self.session_active,
            "session_started_at": (
                self.session_started_at.isoformat() if self.session_started_at else None
            ),
            "notes": self.notes,
        }
