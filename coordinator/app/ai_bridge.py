from __future__ import annotations

from .config import settings


def ask_local(question: str) -> dict:
    return {
        "provider": "ollama",
        "base_url": settings.ollama_base_url,
        "answer": f"Local review placeholder received: {question}",
    }


def ask_openai(question: str) -> dict:
    if not settings.openai_enabled:
        return {"provider": "openai", "allowed": False, "answer": "OpenAI escalation is disabled."}
    return {
        "provider": "openai",
        "allowed": True,
        "budget_usd": settings.openai_monthly_budget_usd,
        "daily_limit_usd": settings.openai_daily_limit_usd,
        "escalation_only": True,
        "answer": f"Rare OpenAI escalation placeholder received: {question}",
    }
