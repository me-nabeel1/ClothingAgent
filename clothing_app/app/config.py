"""Environment configuration for the clothing application service."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Settings required to run the local clothing application API."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        env_prefix="CLOTHING_APP_",
        extra="ignore",
    )

    app_name: str = "Clothing Demo Application"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    log_max_bytes: int = Field(default=5_000_000, ge=100_000)
    log_backup_count: int = Field(default=5, ge=1, le=20)

    database_url: str = (
        "postgresql+asyncpg://postgres:pgadmin@127.0.0.1:5432/ClothingAppDummyDB"
    )
    database_pool_size: int = Field(default=5, ge=1, le=30)
    database_max_overflow: int = Field(default=5, ge=0, le=30)

    cart_ttl_hours: int = Field(default=24, gt=0, le=168)
    product_images_dir: Path = Path("local/product_images")


@lru_cache
def get_config() -> AppConfig:
    """Return one cached configuration object for the process."""

    return AppConfig()
