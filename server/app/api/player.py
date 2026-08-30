"""Player-related endpoints (login, profile, register, logout, etc.)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["player"], prefix="/player")
logger = logging.getLogger(__name__)


def _ok(result: int = 1, **extra: Any) -> dict[str, Any]:
    return {"result": result, **extra}


def _not_implemented(endpoint: str, headers: dict[str, Any] | None = None) -> JSONResponse:
    resp_headers = {"x-legacy-compat": "false"}
    if headers:
        resp_headers.update(headers)
    return JSONResponse(
        status_code=501,
        content={"error": "not_implemented", "endpoint": endpoint, "corrid": str(uuid.uuid4())},
        headers=resp_headers,
    )


def _galaxy_headers(x_galaxy_api_id: str) -> dict[str, str]:
    headers = {"x-galaxy-api": "*/*"}
    if x_galaxy_api_id:
        headers["x-galaxy-api-id"] = x_galaxy_api_id
    return headers


async def _get_active_profile_uuid(db: AsyncSession) -> str | None:
    from app.db.repositories.local_profile_repository import LocalProfileRepository

    repo = LocalProfileRepository(db)
    active = await repo.get_active_session()
    return active.profile_uuid if active else None


@router.post("/profile/load")
async def profile_load(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    nesys_id = body.get("nesys_id")
    if not nesys_id:
        return _ok(result=0)

    try:
        row = await db.execute(
            text(
                "SELECT id, name, level, exp, gold, jewels FROM players WHERE nesys_id = :nid LIMIT 1"
            ),
            {"nid": nesys_id},
        )
        r = row.mappings().first()
        if r:
            return _ok(
                player_id=str(r["id"]),
                name=r["name"],
                level=r["level"],
                exp=r["exp"],
                gold=r["gold"],
                jewels=r["jewels"],
                progresses=[],
                items=[],
            )
    except Exception as exc:
        logger.warning("profile/load DB error: %s", exc)

    return _ok(player_id="", name="", level=1, exp=0, gold=0, jewels=0, progresses=[], items=[])


@router.post("/login")
async def player_login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    player_id = body.get("player_id")
    logger.info("Player login: %s", player_id)

    try:
        await db.execute(
            text("UPDATE players SET last_login = :now WHERE id = :pid"),
            {"pid": player_id, "now": datetime.now(timezone.utc)},
        )
        await db.commit()
    except Exception as exc:
        logger.warning("player/login DB update failed: %s", exc)

    return _ok(
        player_id=player_id or "",
        progresses=[],
        login_bonuses=[],
    )


@router.post("/login_bonus")
async def player_login_bonus(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/player/login_bonus", headers)
    return JSONResponse(
        content={"result": 1, "login_bonuses": [], "update_items": {}}, headers=headers
    )


@router.post("/logout")
async def player_logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/player/logout", headers)
    await capture_request_metadata(request, "/player/logout", resp.status_code, profile_uuid)
    return resp


@router.post("/register")
async def player_register(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> dict[str, Any]:
    response.headers["x-galaxy-api"] = "*/*"
    if x_galaxy_api_id:
        response.headers["x-galaxy-api-id"] = x_galaxy_api_id

    body = await request.json()
    nesys_id = body.get("nesys_id", "")
    name = body.get("name", "Player")

    try:
        await db.execute(
            text(
                "INSERT INTO players (nesys_id, name, level, exp, gold, jewels, created_at, last_login) "
                "VALUES (:nid, :name, 1, 0, 0, 0, :now, :now) "
                "ON CONFLICT (nesys_id) DO UPDATE SET name = :name"
            ),
            {"nid": nesys_id, "name": name, "now": datetime.now(timezone.utc)},
        )
        await db.commit()
    except Exception as exc:
        logger.warning("player/register DB error: %s", exc)

    return _ok(player_id="", name=name, level=1, exp=0, gold=0, jewels=0)


@router.post("/{path:path}")
async def player_fallback(
    path: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    endpoint = f"/player/{path}"
    logger.debug("Unimplemented player endpoint: %s", endpoint)
    if settings.legacy_compatibility_mode:
        resp = JSONResponse(content=_ok(), headers=headers)
    else:
        resp = _not_implemented(endpoint, headers)
    await capture_request_metadata(request, endpoint, resp.status_code, profile_uuid)
    return resp
