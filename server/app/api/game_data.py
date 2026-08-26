"""Game data endpoints (POST /game_data/*)."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["game_data"], prefix="/game_data")
logger = logging.getLogger(__name__)


def _ok(**extra: Any) -> dict[str, Any]:
    return {"result": 1, **extra}


def _not_implemented(endpoint: str, headers: dict[str, Any] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={"error": "not_implemented", "endpoint": endpoint, "corrid": str(uuid.uuid4())},
        headers=headers,
    )


def _galaxy_headers(x_galaxy_api_id: str) -> dict[str, str]:
    headers = {"x-galaxy-api": "*/*"}
    if x_galaxy_api_id:
        headers["x-galaxy-api-id"] = x_galaxy_api_id
    return headers


@router.post("/load")
async def game_data_load(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/game_data/load", headers)
    return JSONResponse(content=_ok(game_data={}), headers=headers)


@router.post("/load/mission")
async def game_data_load_mission(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/game_data/load/mission", headers)
    return JSONResponse(content=_ok(missions=[]), headers=headers)


@router.post("/save")
async def game_data_save(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/game_data/save", headers)
    return JSONResponse(content=_ok(), headers=headers)


@router.post("/{path:path}")
async def game_data_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented game_data endpoint: /game_data/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/game_data/{path}", headers)
    return JSONResponse(content=_ok(), headers=headers)
