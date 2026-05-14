from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .db import connect
from .models import WorkerMode


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_worker(
    node_name: str, mode: WorkerMode, capabilities: list[str], data_profile: dict[str, Any]
) -> dict[str, Any]:
    with connect() as db:
        db.execute(
            """
            INSERT INTO workers(
              node_name, mode, capabilities_json, status, last_heartbeat,
              ohlcv_exists, bbo_exists, ohlcv_size_bytes, bbo_size_bytes,
              ohlcv_sha256, bbo_sha256, first_timestamp, last_timestamp, approximate_row_count
            )
            VALUES(?, ?, ?, 'online', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(node_name) DO UPDATE SET
              mode=excluded.mode,
              capabilities_json=excluded.capabilities_json,
              status='online',
              last_heartbeat=excluded.last_heartbeat,
              ohlcv_exists=excluded.ohlcv_exists,
              bbo_exists=excluded.bbo_exists,
              ohlcv_size_bytes=excluded.ohlcv_size_bytes,
              bbo_size_bytes=excluded.bbo_size_bytes,
              ohlcv_sha256=excluded.ohlcv_sha256,
              bbo_sha256=excluded.bbo_sha256,
              first_timestamp=excluded.first_timestamp,
              last_timestamp=excluded.last_timestamp,
              approximate_row_count=excluded.approximate_row_count
            """,
            (
                node_name,
                mode.value,
                json.dumps(capabilities),
                now(),
                int(data_profile["ohlcv_exists"]),
                int(data_profile["bbo_exists"]),
                int(data_profile["ohlcv_size_bytes"]),
                int(data_profile["bbo_size_bytes"]),
                data_profile["ohlcv_sha256"],
                data_profile["bbo_sha256"],
                data_profile["first_timestamp"],
                data_profile["last_timestamp"],
                int(data_profile["approximate_row_count"]),
            ),
        )
        db.execute(
            "INSERT INTO worker_events(node_name, event, created_at) VALUES(?, ?, ?)",
            (node_name, "register_with_data_profile", now()),
        )
    return {"ok": True, "node_name": node_name}


def heartbeat(node_name: str, mode: WorkerMode) -> dict[str, Any]:
    with connect() as db:
        db.execute(
            "UPDATE workers SET mode=?, status='online', last_heartbeat=? WHERE node_name=?",
            (mode.value, now(), node_name),
        )
    return {"ok": True}


def set_worker_mode(node_name: str, mode: WorkerMode) -> dict[str, Any]:
    with connect() as db:
        db.execute("UPDATE workers SET mode=? WHERE node_name=?", (mode.value, node_name))
    return {"ok": True, "node_name": node_name, "mode": mode.value}


def create_run(name: str, config: dict[str, Any]) -> dict[str, Any]:
    with connect() as db:
        cur = db.execute(
            "INSERT INTO runs(name, status, config_json, created_at) VALUES(?, 'created', ?, ?)",
            (name, json.dumps(config), now()),
        )
        run_id = cur.lastrowid
    return {"run_id": run_id, "status": "created"}


def update_run(run_id: int, status: str) -> dict[str, Any]:
    with connect() as db:
        db.execute("UPDATE runs SET status=?, updated_at=? WHERE id=?", (status, now(), run_id))
    return {"run_id": run_id, "status": status}


def current_run() -> dict[str, Any]:
    with connect() as db:
        row = db.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    return {"run": dict(row) if row else None}


def generate_jobs_for_run(run_id: int, payload: dict[str, Any]) -> list[dict[str, Any]]:
    stages = ["S1", "S2", "S3", "AI_REVIEW"]
    qualified_ids = payload.get("qualified_strategy_ids", [])
    if (payload.get("cold_test_allowed", False) and qualified_ids) or payload.get(
        "protected_cold_validation", False
    ):
        stages.append("COLD_TEST")

    created = []
    with connect() as db:
        for i, stage in enumerate(stages):
            row_payload = {
                "stage": stage,
                "population": payload.get("population", "baseline_population"),
                "archetype": payload.get("archetype", "mixed"),
                "dataset_range": payload.get("dataset_range", {"start": "2015-02-24", "end": "2026-03-24"}),
                "train_range": payload.get("train_range", {"start": "2015-02-24", "end": "2020-12-31"}),
                "validation_range": payload.get("validation_range", {"start": "2021-01-01", "end": "2023-12-31"}),
                "cold_range": payload.get("cold_range", {"start": "2024-01-01", "end": "2026-03-24"}),
                "seed": int(payload.get("seed", 42)) + i,
                "batch_size": int(payload.get("batch_size", 32)),
                "objective": payload.get("objective", "portfolio_1000_day"),
                "cold_test_allowed": payload.get("cold_test_allowed", False) if stage == "COLD_TEST" else False,
                "protected_validation_job": payload.get("protected_cold_validation", False)
                if stage == "COLD_TEST"
                else False,
                "qualified_strategy_ids": qualified_ids,
            }
            priority = {"S1": 100, "S2": 90, "S3": 80, "COLD_TEST": 70, "AI_REVIEW": 60}[stage]
            cur = db.execute(
                "INSERT INTO jobs(run_id, stage, status, priority, payload_json) VALUES(?, ?, 'queued', ?, ?)",
                (run_id, stage, priority, json.dumps(row_payload)),
            )
            created.append({"job_id": cur.lastrowid, "stage": stage})
    return created


def insert_strategy_correlation(payload: dict[str, Any]) -> int:
    with connect() as db:
        cur = db.execute(
            """
            INSERT INTO strategy_correlations(
              strategy_a_id, strategy_b_id, run_id, return_correlation,
              drawdown_overlap_score, same_day_loss_overlap, same_session_overlap,
              same_regime_overlap, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["strategy_a_id"],
                payload["strategy_b_id"],
                payload.get("run_id"),
                payload["return_correlation"],
                payload["drawdown_overlap_score"],
                payload["same_day_loss_overlap"],
                payload["same_session_overlap"],
                payload["same_regime_overlap"],
                now(),
            ),
        )
    return int(cur.lastrowid)
