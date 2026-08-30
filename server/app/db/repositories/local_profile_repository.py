"""Repository for local profile CRUD operations."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.local_profile import LocalProfile


class LocalProfileRepository:
    """CRUD operations for local profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_profile(
        self,
        display_name: str = "Player",
        preferred_controller_index: int = 0,
        notes: str | None = None,
    ) -> LocalProfile:
        profile = LocalProfile(
            display_name=display_name,
            preferred_controller_index=preferred_controller_index,
            notes=notes,
        )
        self._session.add(profile)
        await self._session.flush()
        await self._session.commit()
        return profile

    async def get_by_id(self, profile_id: int) -> LocalProfile | None:
        result = await self._session.execute(
            select(LocalProfile).where(LocalProfile.id == profile_id)
        )
        return result.scalar_one_or_none()

    async def get_by_uuid(self, profile_uuid: str) -> LocalProfile | None:
        result = await self._session.execute(
            select(LocalProfile).where(LocalProfile.profile_uuid == profile_uuid)
        )
        return result.scalar_one_or_none()

    async def list_profiles(self) -> list[LocalProfile]:
        result = await self._session.execute(
            select(LocalProfile).order_by(LocalProfile.last_used_at.desc())
        )
        return list(result.scalars().all())

    async def update_profile(
        self,
        profile_id: int,
        *,
        display_name: str | None = None,
        preferred_controller_index: int | None = None,
        notes: str | None = None,
    ) -> LocalProfile | None:
        updates: dict[str, object] = {}
        if display_name is not None:
            updates["display_name"] = display_name
        if preferred_controller_index is not None:
            updates["preferred_controller_index"] = preferred_controller_index
        if notes is not None:
            updates["notes"] = notes

        if not updates:
            return await self.get_by_id(profile_id)

        updates["last_used_at"] = datetime.now(timezone.utc)
        await self._session.execute(
            update(LocalProfile)
            .where(LocalProfile.id == profile_id)
            .values(**updates)
        )
        await self._session.flush()
        await self._session.commit()
        return await self.get_by_id(profile_id)

    async def delete_profile(self, profile_id: int) -> bool:
        result = await self._session.execute(
            delete(LocalProfile).where(LocalProfile.id == profile_id)
        )
        await self._session.flush()
        await self._session.commit()
        rowcount: int = result.rowcount or 0  # type: ignore[attr-defined]
        return rowcount > 0

    async def record_tutorial_attempt(
        self,
        profile_id: int,
        result: str,
        completed: bool = False,
    ) -> LocalProfile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return None

        profile.tutorial_attempts += 1
        profile.tutorial_last_result = result
        if completed:
            profile.tutorial_completed = True
        profile.last_used_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.commit()
        return profile

    async def start_session(self, profile_id: int) -> LocalProfile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return None

        profile.session_active = True
        profile.session_started_at = datetime.now(timezone.utc)
        profile.last_used_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.commit()
        return profile

    async def end_session(self, profile_id: int) -> LocalProfile | None:
        profile = await self.get_by_id(profile_id)
        if profile is None:
            return None

        profile.session_active = False
        profile.session_started_at = None
        profile.last_used_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.commit()
        return profile

    async def get_active_session(self) -> LocalProfile | None:
        result = await self._session.execute(
            select(LocalProfile).where(LocalProfile.session_active)
        )
        return result.scalar_one_or_none()
