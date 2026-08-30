"""Local profile API endpoints.

These endpoints manage operator-owned local profiles.
They are entirely separate from NESYS authentication, NESiCA identity,
vendor certificates, production matching, production entitlement,
and payment systems.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.local_profile_repository import LocalProfileRepository
from app.dependencies import get_db_session

router = APIRouter(prefix="/profile", tags=["profile"])


def _error(message: str, status: int = 400) -> dict[str, Any]:
    return {"error": True, "message": message, "status": status}


def _ok(data: dict[str, Any] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"error": False, "status": 0}
    if data:
        result.update(data)
    return result


@router.post("/local/create")
async def create_profile(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Create a new local profile."""
    try:
        body = await request.json()
    except Exception:
        body = {}

    display_name = body.get("display_name", "Player")
    controller_index = body.get("preferred_controller_index", 0)
    notes = body.get("notes")

    if not isinstance(display_name, str) or not display_name.strip():
        return _error("display_name must be a non-empty string")
    display_name = display_name.strip()[:32]

    repo = LocalProfileRepository(session)
    profile = await repo.create_profile(
        display_name=display_name,
        preferred_controller_index=controller_index,
        notes=notes,
    )

    return _ok({"profile": profile.to_dict()})


@router.post("/local/list")
async def list_profiles(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """List all local profiles."""
    repo = LocalProfileRepository(session)
    profiles = await repo.list_profiles()
    return _ok({"profiles": [p.to_dict() for p in profiles]})


@router.post("/local/select")
async def select_profile(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Select a profile and start a local session."""
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")

    profile_id = body.get("profile_id")
    if profile_id is None:
        return _error("profile_id is required")

    repo = LocalProfileRepository(session)
    profile = await repo.get_by_id(int(profile_id))
    if profile is None:
        return _error("Profile not found", 404)

    # End any existing active session
    active = await repo.get_active_session()
    if active is not None:
        await repo.end_session(active.id)

    # Start session for selected profile
    profile = await repo.start_session(profile.id)

    return _ok({"profile": profile.to_dict() if profile else None})


@router.post("/local/end")
async def end_session(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """End the current local session."""
    repo = LocalProfileRepository(session)
    active = await repo.get_active_session()
    if active is None:
        return _error("No active session")

    profile = await repo.end_session(active.id)
    return _ok({"profile": profile.to_dict() if profile else None})


@router.post("/local/update")
async def update_profile(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Update a local profile."""
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")

    profile_id = body.get("profile_id")
    if profile_id is None:
        return _error("profile_id is required")

    repo = LocalProfileRepository(session)
    profile = await repo.update_profile(
        int(profile_id),
        display_name=body.get("display_name"),
        preferred_controller_index=body.get("preferred_controller_index"),
        notes=body.get("notes"),
    )

    if profile is None:
        return _error("Profile not found", 404)

    return _ok({"profile": profile.to_dict()})


@router.post("/local/delete")
async def delete_profile(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Delete a local profile."""
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")

    profile_id = body.get("profile_id")
    if profile_id is None:
        return _error("profile_id is required")

    repo = LocalProfileRepository(session)
    deleted = await repo.delete_profile(int(profile_id))
    if not deleted:
        return _error("Profile not found", 404)

    return _ok({"deleted": True})


@router.post("/local/tutorial/record")
async def record_tutorial(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Record a tutorial attempt for a profile."""
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")

    profile_id = body.get("profile_id")
    result = body.get("result", "unknown")
    completed = body.get("completed", False)

    if profile_id is None:
        return _error("profile_id is required")

    repo = LocalProfileRepository(session)
    profile = await repo.record_tutorial_attempt(
        int(profile_id), result=result, completed=completed
    )

    if profile is None:
        return _error("Profile not found", 404)

    return _ok({"profile": profile.to_dict()})
