from __future__ import annotations

import json

from fastapi import APIRouter

from ..aggregator import best_portfolios, score_portfolio_candidate
from ..coordinator import insert_strategy_correlation, now
from ..db import connect
from ..schemas import PortfolioCorrelation, PortfolioMetrics

router = APIRouter(prefix="/portfolios")


@router.get("/best")
def best():
    return {"portfolios": best_portfolios()}


@router.post("/score")
def score(payload: PortfolioMetrics):
    fitness, warnings = score_portfolio_candidate(
        payload.combined_avg_daily_profit,
        payload.combined_max_intraday_dd,
        payload.combined_cold_retention,
        payload.combined_breach_rate,
        payload.correlation_score,
        payload.session_overlap_score,
        payload.regime_overlap_score,
    )
    with connect() as db:
        db.execute(
            """
            INSERT OR REPLACE INTO portfolio_candidates(
              portfolio_id, run_id, strategy_ids_json, combined_avg_daily_profit,
              combined_max_intraday_dd, combined_cold_retention, combined_breach_rate,
              correlation_score, session_overlap_score, regime_overlap_score,
              portfolio_fitness, warning_flags_json, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.portfolio_id,
                payload.run_id,
                json.dumps(payload.strategy_ids),
                payload.combined_avg_daily_profit,
                payload.combined_max_intraday_dd,
                payload.combined_cold_retention,
                payload.combined_breach_rate,
                payload.correlation_score,
                payload.session_overlap_score,
                payload.regime_overlap_score,
                fitness,
                json.dumps(warnings),
                now(),
            ),
        )
    return {"portfolio_id": payload.portfolio_id, "portfolio_fitness": fitness, "warning_flags": warnings}


@router.post("/correlation")
def correlation(payload: PortfolioCorrelation):
    row_id = insert_strategy_correlation(payload.model_dump())
    return {"id": row_id, "ok": True}
