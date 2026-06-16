from __future__ import annotations

import os
from dataclasses import dataclass, field


def _split_csv(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    environment: str = field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    cors_origins: list[str] = field(
        default_factory=lambda: _split_csv(os.getenv("CORS_ORIGINS"), ["http://localhost:3000"])
    )
    max_image_bytes: int = field(
        default_factory=lambda: _int_env("MAX_IMAGE_BYTES", 8 * 1024 * 1024)
    )
    rate_limit_per_minute: int = field(
        default_factory=lambda: _int_env("RATE_LIMIT_PER_MINUTE", 60)
    )
    nominatim_url: str = field(
        default_factory=lambda: os.getenv(
            "NOMINATIM_URL", "https://nominatim.openstreetmap.org/search"
        )
    )
    nominatim_user_agent: str = field(
        default_factory=lambda: os.getenv(
            "NOMINATIM_USER_AGENT", "flipbook-modal-backend/0.1"
        )
    )
    nominatim_timeout_seconds: float = field(
        default_factory=lambda: _float_env("NOMINATIM_TIMEOUT_SECONDS", 5.0)
    )
    nominatim_min_interval_seconds: float = field(
        default_factory=lambda: _float_env("NOMINATIM_MIN_INTERVAL_SECONDS", 1.0)
    )
    geocode_cache_seconds: int = field(
        default_factory=lambda: _int_env("GEOCODE_CACHE_SECONDS", 24 * 60 * 60)
    )
