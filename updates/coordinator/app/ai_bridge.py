from __future__ import annotations

from .config import settings
from .db import connect


def ask_local(question: str) -> dict:
    return {
        "provider": "ollama",
        "base_url": settings.ollama_base_url,
        "answer": f"Local review placeholder received: {question}",
    }


def ask_openai(question: str, escalation_reason: str | None = None, explicit_escalation: bool = False) -> dict:
    if not explicit_escalation:
        return {
            "provider": "openai",
            "allowed": False,
            "answer": "OpenAI requires explicit escalation. Use /ask_openai or explicit escalation event.",
        }
    if not settings.openai_enabled:
        response = {"provider": "openai", "allowed": False, "answer": "OpenAI escalation is disabled."}
        estimated_cost = 0.0
    else:
        response = {
        "provider": "openai",
        "allowed": True,
        "budget_usd": settings.openai_monthly_budget_usd,
        "daily_limit_usd": settings.openai_daily_limit_usd,
        "escalation_only": True,
        "reason": escalation_reason or "manual",
        "answer": f"Rare OpenAI escalation placeholder received: {question}",
        }
        estimated_cost = 0.01
    with connect() as db:
        db.execute(
            "INSERT INTO cost_usage(provider, cost_usd) VALUES('openai', ?)",
            (estimated_cost,),
        )
    return response
