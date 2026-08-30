"""Tutorial endpoints (POST /tutorial/*) – 501 with request capture."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Header, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.capture.request_capture import capture_request_metadata
from app.config import settings
from app.dependencies import get_db_session

router = APIRouter(tags=["tutorial"], prefix="/tutorial")
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


@router.post("/record")
async def tutorial_record(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/tutorial/record", headers)
    await capture_request_metadata(request, "/tutorial/record", resp.status_code, profile_uuid)
    return resp


@router.post("/skip_record")
async def tutorial_skip_record(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    resp = _not_implemented("/tutorial/skip_record", headers)
    await capture_request_metadata(request, "/tutorial/skip_record", resp.status_code, profile_uuid)
    return resp


@router.post("/{path:path}")
async def tutorial_fallback(
    path: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    x_galaxy_api_id: str = Header(default=""),
) -> Response:
    headers = _galaxy_headers(x_galaxy_api_id)
    profile_uuid = await _get_active_profile_uuid(db)
    endpoint = f"/tutorial/{path}"
    logger.debug("Unimplemented tutorial endpoint: %s", endpoint)
    if settings.legacy_compatibility_mode:
        resp = JSONResponse(content={"result": 1}, headers=headers)
    else:
        resp = _not_implemented(endpoint, headers)
    await capture_request_metadata(request, endpoint, resp.status_code, profile_uuid)
    return resp
