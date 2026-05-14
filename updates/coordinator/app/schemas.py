from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .models import WorkerMode


class WorkerDataProfile(BaseModel):
    ohlcv_exists: bool
    bbo_exists: bool
    ohlcv_size_bytes: int
    bbo_size_bytes: int
    ohlcv_sha256: str
    bbo_sha256: str
    first_timestamp: str
    last_timestamp: str
    approximate_row_count: int


class WorkerRegister(BaseModel):
    node_name: str
    mode: WorkerMode
    capabilities: list[str] = Field(default_factory=list)
    data_profile: WorkerDataProfile


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
    strategy_metrics: dict[str, Any] | None = None


class JobFail(BaseModel):
    job_id: int
    error: str
    recoverable: bool = True


class RunCreate(BaseModel):
    name: str = "default"
    config: dict[str, Any] = Field(default_factory=dict)


class GenerateJobsRequest(BaseModel):
    population: str = "baseline_population"
    archetype: str = "mixed"
    dataset_range: dict[str, str] = Field(
        default_factory=lambda: {"start": "2015-02-24", "end": "2026-03-24"}
    )
    train_range: dict[str, str] = Field(
        default_factory=lambda: {"start": "2015-02-24", "end": "2020-12-31"}
    )
    validation_range: dict[str, str] = Field(
        default_factory=lambda: {"start": "2021-01-01", "end": "2023-12-31"}
    )
    cold_range: dict[str, str] = Field(
        default_factory=lambda: {"start": "2024-01-01", "end": "2026-03-24"}
    )
    seed: int = 42
    batch_size: int = 32
    objective: str = "portfolio_1000_day"
    cold_test_allowed: bool = False
    qualified_strategy_ids: list[str] = Field(default_factory=list)
    protected_cold_validation: bool = False


class AiQuestion(BaseModel):
    question: str
    escalation_reason: str | None = None
    explicit_escalation: bool = False


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


class PortfolioCorrelation(BaseModel):
    strategy_a_id: str
    strategy_b_id: str
    run_id: int | None = None
    return_correlation: float
    drawdown_overlap_score: float
    same_day_loss_overlap: float
    same_session_overlap: float
    same_regime_overlap: float
