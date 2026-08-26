"""Health and readiness endpoints for SQLite-only operation."""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_active_engine, get_db_session, is_memory_database

router = APIRouter(tags=["health"])

REQUIRED_TABLES = {
    "player",
    "player_buddies",
    "player_buddy_win_poses",
    "player_emblem_parts",
    "player_emblems",
    "player_line_colors",
    "player_logins",
    "player_mecha_colors",
    "player_mecha_set_parts",
    "player_mecha_sets",
    "player_missions",
    "player_options",
    "player_progress",
    "player_side_weapons",
    "player_titles",
    "player_weapon_set",
    "player_weapon_set_slots",
}


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    errors: list[str] = []

    # Check if we're using an in-memory database
    try:
        engine = get_active_engine()
        in_memory = is_memory_database(engine)
    except Exception:
        in_memory = True

    # 1. Database connection
    try:
        row = await db.execute(text("SELECT 1"))
        row.scalar()
    except Exception:
        errors.append("database_connection")

    # 2. Database file accessibility (skip for in-memory databases)
    if not in_memory:
        try:
            engine = get_active_engine()
            url_str = str(engine.url)
            parsed = urlparse(url_str)
            db_path = Path(unquote(parsed.path))
            if not db_path.exists():
                errors.append("database_file_missing")
            elif not os.access(db_path, os.R_OK | os.W_OK):
                errors.append("database_file_not_writable")
        except Exception:
            errors.append("database_path_check_failed")

    # 3. Required schema
    try:
        result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        existing = {row[0] for row in result.fetchall()}
        missing = REQUIRED_TABLES - existing
        if missing:
            errors.append(f"missing_tables:{','.join(sorted(missing))}")
    except Exception:
        errors.append("schema_check_failed")

    # 4. foreign_keys
    try:
        row = await db.execute(text("PRAGMA foreign_keys"))
        fk = row.scalar()
        if str(fk) != "1":
            errors.append("foreign_keys_disabled")
    except Exception:
        errors.append("foreign_keys_check_failed")

    # 5. journal_mode (skip for in-memory databases)
    if not in_memory:
        try:
            row = await db.execute(text("PRAGMA journal_mode"))
            jm = str(row.scalar())
            if jm.lower() != "wal":
                errors.append(f"journal_mode_not_wal:{jm}")
        except Exception:
            errors.append("journal_mode_check_failed")

    if errors:
        return {"status": "not ready", "errors": ",".join(errors)}

    return {"status": "ready", "database": "sqlite_ok"}
