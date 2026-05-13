from __future__ import annotations

from .config import settings


def redis_url() -> str:
    return settings.redis_url
