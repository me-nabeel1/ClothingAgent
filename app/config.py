import os
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

    # Individual PostgreSQL config fields
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="pgadmin")
    postgres_host: str = Field(default="127.0.0.1")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="ClothingAppDummyDB")

    database_url: str | None = None
    database_pool_size: int = Field(default=5, ge=1, le=30)
    database_max_overflow: int = Field(default=5, ge=0, le=30)

    cart_ttl_hours: int = Field(default=24, gt=0, le=168)
    product_images_dir: Path = Path("local/product_images")

    def model_post_init(self, __context) -> None:
        """Resolve final database URL prioritizing environment variables."""
        if not self.database_url:
            env_url = (
                os.getenv("CLOTHING_APP_DATABASE_URL")
                or os.getenv("DATABASE_URL")
                or os.getenv("POSTGRES_URL")
            )
            if env_url:
                self.database_url = env_url
            else:
                user = os.getenv("POSTGRES_USER", self.postgres_user)
                pwd = os.getenv("POSTGRES_PASSWORD", self.postgres_password)
                host = os.getenv("POSTGRES_HOST", self.postgres_host)
                port = os.getenv("POSTGRES_PORT", str(self.postgres_port))
                db = os.getenv("POSTGRES_DB", self.postgres_db)
                self.database_url = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"


@lru_cache
def get_config() -> AppConfig:
    """Return one cached configuration object for the process."""

    return AppConfig()
