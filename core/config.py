"""Centralized configuration loaded from environment variables.

Uses pydantic-settings to provide a single source of truth for all
configurable values.  Falls back to sensible defaults for local development.

Attributes:
    api_keys: Comma-separated API keys for backend auth (empty = no auth).
    allowed_origins: Comma-separated CORS origins.
    primary_model: Primary Gemini model identifier.
    secondary_model: Fallback Gemini model identifier.
    llm_timeout: Timeout in seconds for LLM calls.
    rate_limit_rpm: Max requests per minute per IP.
    cache_ttl: Cache time-to-live in seconds.
    cache_max_size: Maximum number of cached entries.
    cb_threshold: Circuit breaker failure threshold.
    cb_cooldown: Circuit breaker cooldown in seconds.
    cb_half_open_max: Max probes in half-open state.
    data_dir: Path to data directory (relative to project root).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields map 1:1 to environment variable names (uppercase).
    Defaults match the values used in the original monolithic orchestrator.

    Pydantic BaseSettings handles:
        - Loading from .env file automatically
        - Type coercion (str → int, etc.)
        - Validation (optional: you can add constraints)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- API Security ---
    api_keys: str = ""
    allowed_origins: str = "http://localhost:3000,http://localhost:7860,https://vernacular-bridge-six.vercel.app,https://vernacular-bridge-r36ygnixx-andrew-a545.vercel.app"

    # --- LLM Configuration ---
    primary_model: str = "gemini-3.5-flash-lite"
    secondary_model: str = "gemini-3.8-flash"
    llm_timeout: int = 30
    google_api_key: str = ""

    # --- Rate Limiting ---
    rate_limit_rpm: int = 20

    # --- Caching ---
    cache_ttl: int = 600
    cache_max_size: int = 100

    # --- Circuit Breaker ---
    cb_threshold: int = 3
    cb_cooldown: int = 60
    cb_half_open_max: int = 1

    # --- Data ---
    data_dir: str = "data"


# Module-level singleton — import and use directly.
# Usage: from core.config import settings; settings.primary_model
settings = Settings()
