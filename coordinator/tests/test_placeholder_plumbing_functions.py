import os
import json
import tempfile
import unittest
from types import SimpleNamespace

from app import db, job_queue
from app.coordinator import create_run, generate_jobs_for_run, register_worker
from app.models import WorkerMode


class PlaceholderPlumbingFunctionTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "project01.db")
        db.settings = SimpleNamespace(database_path=self.db_path)
        job_queue.settings = SimpleNamespace(
            expected_ohlcv_sha256="",
            expected_bbo_sha256="",
        )
        db.init_db()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_placeholder_loop_stores_completed_result(self):
        run_id = create_run("plumbing", {})["run_id"]
        created = generate_jobs_for_run(
            run_id,
            {
                "cold_test_allowed": True,
                "qualified_strategy_ids": ["qualified-1"],
            },
        )
        self.assertTrue(created)

        register_worker(
            "OPTIMUS",
            WorkerMode.full_worker,
            ["S1", "S2", "S3", "COLD_TEST", "AI_REVIEW"],
            {
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
        )

        claimed = job_queue.claim_job("OPTIMUS", WorkerMode.full_worker)["job"]
        self.assertIsNotNone(claimed)
        job_queue.complete_job(
            claimed["id"],
            fitness=1.0,
            summary="placeholder",
            cold_test_used=False,
            strategy_metrics=None,
        )

        with db.connect() as conn:
            job_row = conn.execute("SELECT * FROM jobs WHERE id=?", (claimed["id"],)).fetchone()
            result_row = conn.execute(
                "SELECT * FROM strategy_results WHERE job_id=? ORDER BY id DESC LIMIT 1",
                (claimed["id"],),
            ).fetchone()

        self.assertEqual(job_row["status"], "completed")
        self.assertIsNotNone(result_row)
        self.assertEqual(result_row["fitness"], 1.0)
        self.assertEqual(result_row["summary"], "placeholder")
        self.assertEqual(result_row["cold_test_used"], 0)
        self.assertEqual(result_row["worker_name"], "OPTIMUS")
        self.assertEqual(result_row["stage"], claimed["stage"])
        payload_json = json.loads(result_row["payload_json"])
        result_json = json.loads(result_row["result_json"])
        self.assertEqual(payload_json["stage"], claimed["stage"])
        self.assertEqual(result_json["fitness"], 1.0)
        self.assertEqual(result_json["summary"], "placeholder")
        self.assertFalse(result_json["cold_test_used"])


if __name__ == "__main__":
    unittest.main()
