from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    cluster_token: str = os.getenv("PROJECT01_CLUSTER_TOKEN", "dev-token")
    database_path: str = os.getenv("PROJECT01_DB_PATH", "/opt/project01/state/project01.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    openai_enabled: bool = os.getenv("OPENAI_ENABLED", "false").lower() in {"1", "true", "y", "yes"}
    openai_monthly_budget_usd: float = float(os.getenv("OPENAI_MONTHLY_BUDGET_USD", "5"))
    openai_daily_limit_usd: float = float(os.getenv("OPENAI_DAILY_HARD_LIMIT_USD", "0.25"))


settings = Settings()
