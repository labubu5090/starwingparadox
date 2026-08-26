"""Game data endpoints (POST /game_data/*)."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

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


@router.post("/load")
async def game_data_load(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    return _not_implemented("/game_data/load", headers)


@router.post("/load/mission")
async def game_data_load_mission(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    return _not_implemented("/game_data/load/mission", headers)


@router.post("/save")
async def game_data_save(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    return _not_implemented("/game_data/save", headers)


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
    return JSONResponse(content={"result": 1}, headers=headers)
