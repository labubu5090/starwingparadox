"""Game data endpoints (POST /game_data/*) with request capture."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["game_data"], prefix="/game_data")
logger = logging.getLogger(__name__)


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


@router.post("/load")
async def game_data_load(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/game_data/load", headers)
    await capture_request_metadata(request, "/game_data/load", resp.status_code, profile_uuid)
    return resp


@router.post("/load/mission")
async def game_data_load_mission(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/game_data/load/mission", headers)
    await capture_request_metadata(
        request, "/game_data/load/mission", resp.status_code, profile_uuid
    )
    return resp


@router.post("/save")
async def game_data_save(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/game_data/save", headers)
    await capture_request_metadata(request, "/game_data/save", resp.status_code, profile_uuid)
    return resp


@router.post("/{path:path}")
async def game_data_fallback(
    path: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    endpoint = f"/game_data/{path}"
    logger.debug("Unimplemented game_data endpoint: %s", endpoint)
    if settings.legacy_compatibility_mode:
        resp = JSONResponse(content={"result": 1}, headers=headers)
    else:
        resp = _not_implemented(endpoint, headers)
    await capture_request_metadata(request, endpoint, resp.status_code, profile_uuid)
    return resp
