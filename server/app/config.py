"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 4001
    pb_port: int = 6666
    database_url: str = "postgresql+psycopg://paradox:changeme@localhost:5432/paradox"
    redis_url: str = "redis://localhost:6379/0"
    pb_timeout: float = 30.0
    log_level: str = "INFO"
    protocol_raw_logging: bool = False
    protocol_hash_logging: bool = True
    legacy_compatibility_mode: bool = True
    matcher_hostname: str = "paradox.yourdomain.com"
    version_main: int = 70571
    version_data: int = 70571

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
