import os
import tempfile
import unittest
from types import SimpleNamespace

from app import db
from app.coordinator import generate_jobs_for_run


class JobGenerationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "project01.db")
        db.settings = SimpleNamespace(database_path=self.db_path)
        db.init_db()
        with db.connect() as conn:
            conn.execute(
                "INSERT INTO runs(name, status, config_json, created_at) VALUES('r1', 'created', '{}', '2024-01-01T00:00:00+00:00')"
            )

    def tearDown(self):
        self.tempdir.cleanup()

    def test_generate_jobs_creates_expected_stages(self):
        payload = {
            "cold_test_allowed": True,
            "qualified_strategy_ids": ["strat-1"],
        }
        result = {"created_jobs": generate_jobs_for_run(1, payload)}
        stages = [j["stage"] for j in result["created_jobs"]]
        self.assertEqual(stages, ["S1", "S2", "S3", "AI_REVIEW", "COLD_TEST"])


if __name__ == "__main__":
    unittest.main()
