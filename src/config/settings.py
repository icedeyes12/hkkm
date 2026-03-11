"""Application settings with Pydantic validation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(env_prefix="HKKM_DB_")

    url: str = Field(default="sqlite:///hkkm.db")
    echo: bool = Field(default=False, description="Enable SQL logging")
    pool_size: int = Field(default=5, ge=1, le=20)
    timeout: float = Field(default=30.0, description="Connection timeout in seconds")
    wal_mode: bool = Field(default=True, description="Enable WAL mode for better concurrency")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(("sqlite://", "sqlite+aiosqlite://")):
            raise ValueError("Only SQLite databases are supported")
        return v


class TUISettings(BaseSettings):
    """TUI/Terminal UI configuration."""

    model_config = SettingsConfigDict(env_prefix="HKKM_TUI_")

    theme: str = Field(default="default")
    animation_speed: float = Field(default=1.0, ge=0.0, le=5.0)
    enable_mouse: bool = Field(default=True)
    vim_mode: bool = Field(default=False)
    unicode_mode: str = Field(default="auto")
    high_contrast: bool = Field(default=False)
    reduced_motion: bool = Field(default=False)


class GameSettings(BaseSettings):
    """Game mechanics configuration."""

    model_config = SettingsConfigDict(env_prefix="HKKM_GAME_")

    starting_balance: int = Field(default=500, ge=0)
    max_level: int = Field(default=15, ge=1)
    auto_save_interval: int = Field(default=300, ge=30)
    xp_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)
    economy_multiplier: float = Field(default=1.0, ge=0.1, le=10.0)
    enable_debug_mode: bool = Field(default=False)


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # App metadata
    app_name: str = Field(default="Hikikimo Life")
    version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")

    # Paths
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".hkkm")

    # Nested settings
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    tui: TUISettings = Field(default_factory=TUISettings)
    game: GameSettings = Field(default_factory=GameSettings)

    @field_validator("data_dir")
    @classmethod
    def ensure_data_dir(cls, v: Path) -> Path:
        """Ensure data directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def database_path(self) -> Path:
        """Get resolved database path."""
        db_url = self.db.url
        if db_url.startswith("sqlite:///"):
            path_str = db_url.replace("sqlite:///", "")
            if not Path(path_str).is_absolute():
                return self.data_dir / path_str
            return Path(path_str)
        return self.data_dir / "hkkm.db"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ("dev", "development", "test")


# Global settings instance (lazy-loaded)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
