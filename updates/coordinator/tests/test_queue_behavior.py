import os
import tempfile
import unittest
from types import SimpleNamespace

from app import db, job_queue, scheduler


class QueueBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "project01.db")
        db.settings = SimpleNamespace(database_path=self.db_path)
        job_queue.settings = SimpleNamespace(
            expected_ohlcv_sha256="",
            expected_bbo_sha256="",
        )
        scheduler.settings = SimpleNamespace(heartbeat_stale_seconds=90)
        db.init_db()
        with db.connect() as conn:
            conn.execute(
                """
                INSERT INTO workers(
                  node_name, mode, capabilities_json, status, last_heartbeat,
                  ohlcv_exists, bbo_exists, ohlcv_size_bytes, bbo_size_bytes,
                  ohlcv_sha256, bbo_sha256, first_timestamp, last_timestamp, approximate_row_count
                ) VALUES(
                  'OPTIMUS','full_worker','[]','online','2999-01-01T00:00:00+00:00',
                  1,1,100,100,'sha1','sha2','2020-01-01','2026-01-01',10
                )
                """
            )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_claim_empty_job(self):
        result = job_queue.claim_job("OPTIMUS", job_queue.WorkerMode.full_worker)
        self.assertIsNone(result["job"])

    def test_stale_requeue_does_not_requeue_healthy_claimed(self):
        with db.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(run_id, stage, status, claimed_by, claimed_at, attempt_count, max_attempts, payload_json)
                VALUES(1, 'S1', 'claimed', 'OPTIMUS', '2999-01-01T00:00:00+00:00', 0, 3, '{}')
                """
            )
        count = scheduler.requeue_stale_jobs()
        self.assertEqual(count, 0)

    def test_stale_requeue_does_requeue_old_claimed(self):
        with db.connect() as conn:
            conn.execute(
                """
                INSERT INTO jobs(run_id, stage, status, claimed_by, claimed_at, attempt_count, max_attempts, payload_json)
                VALUES(1, 'S1', 'claimed', 'OPTIMUS', '2000-01-01T00:00:00+00:00', 0, 3, '{}')
                """
            )
        count = scheduler.requeue_stale_jobs()
        self.assertEqual(count, 1)

    def test_claim_blocked_for_missing_data(self):
        with db.connect() as conn:
            conn.execute(
                """
                INSERT INTO workers(
                  node_name, mode, capabilities_json, status, last_heartbeat,
                  ohlcv_exists, bbo_exists, ohlcv_size_bytes, bbo_size_bytes,
                  ohlcv_sha256, bbo_sha256, first_timestamp, last_timestamp, approximate_row_count
                ) VALUES(
                  'STARSCREAM','full_worker','[]','online','2999-01-01T00:00:00+00:00',
                  0,1,100,100,'sha1','sha2','2020-01-01','2026-01-01',10
                )
                """
            )
            conn.execute(
                "INSERT INTO jobs(run_id, stage, status, priority, payload_json) VALUES(1, 'S1', 'queued', 100, '{}')"
            )
        result = job_queue.claim_job("STARSCREAM", job_queue.WorkerMode.full_worker)
        self.assertIsNone(result["job"])


if __name__ == "__main__":
    unittest.main()
