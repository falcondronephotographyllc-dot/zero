from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .db import connect
from .models import WorkerMode


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_worker(node_name: str, mode: WorkerMode, capabilities: list[str]) -> dict[str, Any]:
    with connect() as db:
        db.execute(
            """
            INSERT INTO workers(node_name, mode, capabilities_json, status, last_heartbeat)
            VALUES(?, ?, ?, 'online', ?)
            ON CONFLICT(node_name) DO UPDATE SET
              mode=excluded.mode,
              capabilities_json=excluded.capabilities_json,
              status='online',
              last_heartbeat=excluded.last_heartbeat
            """,
            (node_name, mode.value, json.dumps(capabilities), now()),
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
