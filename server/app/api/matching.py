"""Matching / lobby endpoints (POST /matching/*)."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["matching"], prefix="/matching")
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


@router.post("/server")
async def matching_server(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/matching/server", headers)
    return JSONResponse(content=_ok(servers=[]), headers=headers)


@router.post("/match_id/generate")
async def match_id_generate(
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    if not settings.legacy_compatibility_mode:
        return _not_implemented("/matching/match_id/generate", headers)
    return JSONResponse(content=_ok(match_id=""), headers=headers)


@router.post("/{path:path}")
async def matching_fallback(
    path: str,
    request: Request,
    response: Response,
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    logger.debug("Unimplemented matching endpoint: /matching/%s", path)
    if not settings.legacy_compatibility_mode:
        return _not_implemented(f"/matching/{path}", headers)
    return JSONResponse(content=_ok(), headers=headers)
