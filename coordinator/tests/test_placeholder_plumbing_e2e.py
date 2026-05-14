import importlib
import json

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("fastapi.testclient")
from fastapi.testclient import TestClient


def _build_client(monkeypatch, tmp_path):
    db_path = tmp_path / "coordinator-e2e.db"
    monkeypatch.setenv("PROJECT01_ALLOW_DEV_TOKEN", "true")
    monkeypatch.setenv("PROJECT01_CLUSTER_TOKEN", "dev-token")
    monkeypatch.setenv("PROJECT01_DB_PATH", str(db_path))
    monkeypatch.setenv("OPENAI_ENABLED", "false")

    import app.config
    import app.db
    import app.main

    importlib.reload(app.config)
    importlib.reload(app.db)
    importlib.reload(app.main)
    app.db.init_db()
    client = TestClient(app.main.app)
    return client, app.db


def test_placeholder_cluster_plumbing_e2e(monkeypatch, tmp_path):
    client, app_db = _build_client(monkeypatch, tmp_path)
    headers = {"Authorization": "Bearer dev-token"}

    run_res = client.post("/api/runs/create", json={"name": "plumbing", "config": {}}, headers=headers)
    assert run_res.status_code == 200
    run_id = run_res.json()["run_id"]

    gen_res = client.post(
        f"/api/runs/{run_id}/generate-jobs",
        json={"cold_test_allowed": True, "qualified_strategy_ids": ["qualified-1"]},
        headers=headers,
    )
    assert gen_res.status_code == 200
    created_jobs = gen_res.json()["created_jobs"]
    assert created_jobs

    register_payload = {
        "node_name": "OPTIMUS",
        "mode": "full_worker",
        "capabilities": ["S1", "S2", "S3", "COLD_TEST", "AI_REVIEW"],
        "data_profile": {
            "ohlcv_exists": True,
            "bbo_exists": True,
            "ohlcv_size_bytes": 100,
            "bbo_size_bytes": 120,
            "ohlcv_sha256": "sha-ohlcv",
            "bbo_sha256": "sha-bbo",
            "first_timestamp": "2020-01-01",
            "last_timestamp": "2026-01-01",
            "approximate_row_count": 1000,
        },
    }
    reg_res = client.post("/api/workers/register", json=register_payload, headers=headers)
    assert reg_res.status_code == 200

    claim_res = client.post(
        "/api/jobs/claim",
        json={"node_name": "OPTIMUS", "mode": "full_worker", "capabilities": ["S1", "S2", "S3", "COLD_TEST", "AI_REVIEW"]},
        headers=headers,
    )
    assert claim_res.status_code == 200
    job = claim_res.json()["job"]
    assert job is not None

    complete_res = client.post(
        "/api/jobs/complete",
        json={
            "job_id": job["id"],
            "fitness": 1.0,
            "summary": "placeholder",
            "cold_test_used": False,
            "strategy_metrics": None,
        },
        headers=headers,
    )
    assert complete_res.status_code == 200

    with app_db.connect() as conn:
        job_row = conn.execute("SELECT * FROM jobs WHERE id=?", (job["id"],)).fetchone()
        assert job_row["status"] == "completed"
        result_row = conn.execute(
            "SELECT * FROM strategy_results WHERE job_id=? ORDER BY id DESC LIMIT 1",
            (job["id"],),
        ).fetchone()
        assert result_row is not None
        assert result_row["worker_name"] == "OPTIMUS"
        assert result_row["fitness"] == 1.0
        assert result_row["summary"] == "placeholder"
        assert result_row["cold_test_used"] == 0
        assert result_row["stage"] == job["stage"]
        payload_json = json.loads(result_row["payload_json"])
        assert payload_json["stage"] == job["stage"]
        result_json = json.loads(result_row["result_json"])
        assert result_json["fitness"] == 1.0
