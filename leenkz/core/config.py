"""Configuration settings for leenkz."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "Leenkz"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://leenkz:leenkz@localhost/leenkz",
        env="DATABASE_URL"
    )
    
    # CORS
    allowed_hosts: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="ALLOWED_HOSTS"
    )
    
    # Static files
    static_dir: str = Field(
        default="static",
        env="STATIC_DIR"
    )
    
    # Build settings
    build_dir: str = Field(
        default="dist",
        env="BUILD_DIR"
    )
    
    # Snapshot settings
    snapshot_max_size_mb: int = Field(
        default=25,
        env="SNAPSHOT_MAX_SIZE_MB"
    )
    snapshot_allowed_mime_regex: str = Field(
        default=r".*",
        env="SNAPSHOT_ALLOWED_MIME_REGEX"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_static_dir() -> Path:
    """Get the static files directory."""
    package_dir = Path(__file__).parent.parent
    static_dir = package_dir / settings.static_dir
    
    # If static_dir doesn't exist, try to copy from build_dir
    if not static_dir.exists():
        build_dir = Path(settings.build_dir)
        if build_dir.exists():
            import shutil
            shutil.copytree(build_dir, static_dir, dirs_exist_ok=True)
    
    return static_dir 