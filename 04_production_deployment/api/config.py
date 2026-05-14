"""
Centralized configuration for the AdventureWorks Analytics API.

Reads from environment variables with sensible defaults for local development.
Settings are validated and typed via Pydantic.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API configuration sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "AdventureWorks Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Security ---
    # In production, this MUST be set via environment variable, not the default
    api_key: str = "dev-key-change-in-production"
    api_key_header_name: str = "X-API-Key"

    # --- Data paths ---
    project_root: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = project_root / "data" / "processed"
    predictions_dir: Path = project_root / "data" / "predictions"
    models_dir: Path = project_root / "models"

    # --- Reference date for Recency computation ---
    # Matches the date used during model training (notebooks 02, 03)
    reference_date: str = "2014-01-01"

    # --- Logging ---
    log_level: str = "INFO"


# Module-level singleton, imported across the app
settings = Settings()
