from __future__ import annotations

import json

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
        rows = db.execute(
            "SELECT * FROM jobs WHERE status='queued' ORDER BY priority DESC, id ASC"
        ).fetchall()
        for row in rows:
            stage = row["stage"]
            if not mode_accepts(mode, stage):
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


def complete_job(job_id: int, fitness: float, summary: str, cold_test_used: bool) -> dict:
    with connect() as db:
        db.execute(
            "UPDATE jobs SET status='completed', completed_at=?, result_json=? WHERE id=?",
            (now(), json.dumps({"fitness": fitness, "summary": summary, "cold_test_used": cold_test_used}), job_id),
        )
        db.execute(
            "INSERT INTO strategy_results(job_id, fitness, summary, cold_test_used, created_at) VALUES(?, ?, ?, ?, ?)",
            (job_id, fitness, summary, int(cold_test_used), now()),
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
