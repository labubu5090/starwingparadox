"""Master-data fixtures (GET /sw-data/{filename})."""

from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["swdata"])

SWDATA_PATH = Path(__file__).resolve().parents[2] / "sw-data"

NOT_FOUND_BODY = '{"detail":"Not Found"}'
NOT_FOUND_MEDIA = "application/json"


@router.get("/sw-data/{filename}")
async def sw_data(filename: str) -> PlainTextResponse:
    safe_name = unquote(filename)
    if "/" in safe_name or "\\" in safe_name or safe_name.startswith("."):
        raise HTTPException(status_code=404, detail="Not Found")
    target = (SWDATA_PATH / safe_name).resolve()
    if not target.is_relative_to(SWDATA_PATH.resolve()) or not target.is_file():
        return PlainTextResponse(NOT_FOUND_BODY, media_type=NOT_FOUND_MEDIA)
    return PlainTextResponse(
        target.read_bytes().decode("utf-8-sig"),
        media_type="text/csv",
    )