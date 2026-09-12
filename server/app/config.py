"""Application configuration via environment variables."""

from __future__ import annotations

import sys
from urllib.parse import urlparse

from pydantic_settings import BaseSettings

_SQLITE_PREFIXES = ("sqlite", "sqlite+aiosqlite")
_FORBIDDEN_PREFIXES = ("postgresql", "mysql", "mssql", "oracle")


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 4001
    pb_port: int = 6666
    database_url: str = "sqlite+aiosqlite:///./data/starwing.db"
    redis_url: str = "redis://localhost:6379/0"
    pb_timeout: float = 600.0
    log_level: str = "INFO"
    protocol_raw_logging: bool = False
    protocol_hash_logging: bool = True
    legacy_compatibility_mode: bool = True
    private_server_compatibility_mode: bool = False
    matcher_hostname: str = "127.0.0.1"
    version_main: int = 70571
    version_data: int = 70571

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_database_url(self) -> str:
        """Return the database URL, validating it is SQLite-only."""
        url = self.database_url.strip()
        if not url:
            print("FATAL: DATABASE_URL is empty", file=sys.stderr)
            sys.exit(1)
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        if not any(scheme.startswith(p) for p in _SQLITE_PREFIXES):
            print(
                f"FATAL: DATABASE_URL must use SQLite. Got: {scheme}://",
                file=sys.stderr,
            )
            sys.exit(1)
        if "://" in url and parsed.hostname and parsed.hostname not in ("", "localhost"):
            print(
                f"FATAL: SQLite database must be local. Got host: {parsed.hostname}",
                file=sys.stderr,
            )
            sys.exit(1)
        # Fix Windows path resolution for sqlite:/// relative paths
        # urlparse on Windows turns sqlite:///./data/x.db into path=/./data/x.db
        # which resolves to C:\data\x.db instead of CWD/data/x.db
        from pathlib import Path
        from urllib.parse import unquote
        raw_path = unquote(parsed.path)
        if raw_path and not Path(raw_path).is_absolute():
            abs_path = (Path.cwd() / raw_path.lstrip("/\\")).resolve()
            # Rebuild URL: scheme:///absolute_path
            url = f"{parsed.scheme}:///{abs_path.as_posix()}"
        return url


settings = Settings()
