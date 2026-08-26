"""Ranking endpoints (POST /ranking/*)."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["ranking"], prefix="/ranking")
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


@router.post("/national")
async def ranking_national(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/national", headers)
    return JSONResponse(content=_ok(ranking=[]), headers=headers)


@router.post("/location")
async def ranking_location(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/location", headers)
    return JSONResponse(content=_ok(ranking=[]), headers=headers)


@router.post("/prefecture")
async def ranking_prefecture(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/prefecture", headers)
    return JSONResponse(content=_ok(ranking=[]), headers=headers)


@router.post("/event")
async def ranking_event(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/event", headers)
    return JSONResponse(content=_ok(ranking=[]), headers=headers)


@router.post("/weapon")
async def ranking_weapon(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/ranking/weapon", headers)
    return JSONResponse(content=_ok(ranking=[]), headers=headers)


@router.post("/{path:path}")
async def ranking_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented ranking endpoint: /ranking/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/ranking/{path}", headers)
    return JSONResponse(content=_ok(), headers=headers)
