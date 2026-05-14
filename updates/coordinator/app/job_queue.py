from __future__ import annotations

import json

from .config import settings
from .coordinator import now
from .db import connect
from .models import WorkerMode

ROUTING = {
    "S1": ["OPTIMUS", "MEGATRON", "STARSCREAM"],
    "S2": ["MEGATRON", "OPTIMUS", "STARSCREAM"],
    "S3": ["MEGATRON", "OPTIMUS", "STARSCREAM"],
    "COLD_TEST": ["MEGATRON", "OPTIMUS", "STARSCREAM"],
    "AI_REVIEW": ["MEGATRON", "STARSCREAM"],
}


def mode_accepts(mode: WorkerMode, stage: str) -> bool:
    if mode in {WorkerMode.off, WorkerMode.dev_only}:
        return False
    if mode == WorkerMode.light_worker:
        return stage in {"S1", "S2"}
    if mode == WorkerMode.full_worker:
        return stage in {"S1", "S2", "S3", "COLD_TEST", "AI_REVIEW"}
    if mode == WorkerMode.burst_worker:
        return stage in {"S1", "S2", "S3", "AI_REVIEW"}
    return False


def claim_job(node_name: str, mode: WorkerMode) -> dict:
    with connect() as db:
        worker = db.execute("SELECT * FROM workers WHERE node_name=?", (node_name,)).fetchone()
        if worker is None:
            return {"job": None}
        rows = db.execute(
            "SELECT * FROM jobs WHERE status='queued' ORDER BY priority DESC, id ASC"
        ).fetchall()
        for row in rows:
            stage = row["stage"]
            if not mode_accepts(mode, stage):
                continue
            if not worker_data_ready(worker, stage):
                continue
            preferred = ROUTING.get(stage, [])
            if node_name not in preferred:
                continue
            db.execute(
                "UPDATE jobs SET status='claimed', claimed_by=?, claimed_at=? WHERE id=?",
                (node_name, now(), row["id"]),
            )
            return {"job": row_to_job(row)}
    return {"job": None}


def row_to_job(row) -> dict:
    return {
        "id": row["id"],
        "run_id": row["run_id"],
        "stage": row["stage"],
        "payload": json.loads(row["payload_json"] or "{}"),
        "attempt_count": row["attempt_count"],
        "max_attempts": row["max_attempts"],
    }


def complete_job(
    job_id: int,
    fitness: float,
    summary: str,
    cold_test_used: bool,
    strategy_metrics: dict | None = None,
) -> dict:
    with connect() as db:
        job = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        payload_json = job["payload_json"] if job else "{}"
        stage = job["stage"] if job else ""
        worker_name = job["claimed_by"] if job and job["claimed_by"] else ""
        payload = json.loads(payload_json or "{}")
        metrics = strategy_metrics or payload.get("strategy_metrics", {})
        db.execute(
            "UPDATE jobs SET status='completed', completed_at=?, result_json=? WHERE id=?",
            (now(), json.dumps({"fitness": fitness, "summary": summary, "cold_test_used": cold_test_used}), job_id),
        )
        db.execute(
            """
            INSERT INTO strategy_results(
              run_id, job_id, strategy_id, fitness, avg_daily_profit, max_intraday_dd, max_daily_loss,
              cold_retention, mffu_breach_rate, trade_count, best_session, best_regime,
              worker_name, stage, payload_json, result_json, summary, cold_test_used, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job["run_id"] if job else None,
                job_id,
                metrics.get("strategy_id"),
                fitness,
                float(metrics.get("avg_daily_profit", 0)),
                float(metrics.get("max_intraday_dd", 0)),
                float(metrics.get("max_daily_loss", 0)),
                float(metrics.get("cold_retention", 0)),
                float(metrics.get("mffu_breach_rate", 0)),
                int(metrics.get("trade_count", 0)),
                metrics.get("best_session", ""),
                metrics.get("best_regime", ""),
                worker_name,
                stage,
                payload_json or "{}",
                json.dumps({"fitness": fitness, "summary": summary, "cold_test_used": cold_test_used}),
                summary,
                int(cold_test_used),
                now(),
            ),
        )
    return {"ok": True, "job_id": job_id}


def fail_job(job_id: int, error: str, recoverable: bool) -> dict:
    with connect() as db:
        status = "queued" if recoverable else "failed"
        db.execute(
            "UPDATE jobs SET status=?, attempt_count=attempt_count+1, error=? WHERE id=?",
            (status, error, job_id),
        )
    return {"ok": True, "job_id": job_id}


def worker_data_ready(worker_row, stage: str) -> bool:
    # AI review can run without dataset parity.
    if stage == "AI_REVIEW":
        return True
    if stage not in {"S1", "S2", "S3", "COLD_TEST"}:
        return True
    if not worker_row["ohlcv_exists"] or not worker_row["bbo_exists"]:
        return False
    if int(worker_row["ohlcv_size_bytes"]) <= 0 or int(worker_row["bbo_size_bytes"]) <= 0:
        return False
    if not worker_row["first_timestamp"] or not worker_row["last_timestamp"]:
        return False
    if int(worker_row["approximate_row_count"]) <= 0:
        return False
    if settings.expected_ohlcv_sha256 and worker_row["ohlcv_sha256"] != settings.expected_ohlcv_sha256:
        return False
    if settings.expected_bbo_sha256 and worker_row["bbo_sha256"] != settings.expected_bbo_sha256:
        return False
    return True
