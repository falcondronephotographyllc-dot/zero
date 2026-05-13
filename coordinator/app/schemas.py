from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .models import WorkerMode


class WorkerRegister(BaseModel):
    node_name: str
    mode: WorkerMode
    capabilities: list[str] = Field(default_factory=list)


class Heartbeat(BaseModel):
    node_name: str
    mode: WorkerMode


class ModeChange(BaseModel):
    mode: WorkerMode


class JobClaim(BaseModel):
    node_name: str
    mode: WorkerMode
    capabilities: list[str] = Field(default_factory=list)


class JobComplete(BaseModel):
    job_id: int
    fitness: float = 0.0
    summary: str = ""
    cold_test_used: bool = False


class JobFail(BaseModel):
    job_id: int
    error: str
    recoverable: bool = True


class RunCreate(BaseModel):
    name: str = "default"
    config: dict[str, Any] = Field(default_factory=dict)


class AiQuestion(BaseModel):
    question: str


class PortfolioMetrics(BaseModel):
    portfolio_id: str
    run_id: int | None = None
    strategy_ids: list[str]
    combined_avg_daily_profit: float
    combined_max_intraday_dd: float
    combined_cold_retention: float
    combined_breach_rate: float
    correlation_score: float
    session_overlap_score: float
    regime_overlap_score: float
