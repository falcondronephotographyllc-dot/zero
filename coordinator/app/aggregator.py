from __future__ import annotations

from .db import connect


def best_strategies(limit: int = 10) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM strategy_results ORDER BY fitness DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def best_portfolios(limit: int = 10) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM portfolio_candidates ORDER BY portfolio_fitness DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def score_portfolio_candidate(
    combined_avg_daily_profit: float,
    combined_max_intraday_dd: float,
    combined_cold_retention: float,
    combined_breach_rate: float,
    correlation_score: float,
    session_overlap_score: float,
    regime_overlap_score: float,
) -> tuple[float, list[str]]:
    warnings: list[str] = []
    rejected_penalty = 0.0
    if combined_breach_rate > 0:
        warnings.append("mffu_breach")
        rejected_penalty -= 1000.0
    if combined_max_intraday_dd > 800:
        warnings.append("combined_drawdown_over_safety")
    if combined_cold_retention < 0.80:
        warnings.append("cold_retention_below_80pct")
        rejected_penalty -= 1000.0
    if correlation_score > 0.70:
        warnings.append("high_correlation")
    if session_overlap_score > 0.70:
        warnings.append("session_concentration")
    if regime_overlap_score > 0.70:
        warnings.append("regime_concentration")

    target_score = max(0.0, 1.0 - abs(1000.0 - combined_avg_daily_profit) / 1000.0) * 20.0
    drawdown_score = max(-1.0, 1.0 - min(2.0, combined_max_intraday_dd / 800.0)) * 25.0
    cold_score = min(1.25, combined_cold_retention / 0.80) * 20.0
    breach_score = 20.0 if combined_breach_rate == 0 else -100.0
    diversity_score = (1.0 - min(1.0, (correlation_score + session_overlap_score + regime_overlap_score) / 3.0)) * 25.0
    return target_score + drawdown_score + cold_score + breach_score + diversity_score + rejected_penalty, warnings
