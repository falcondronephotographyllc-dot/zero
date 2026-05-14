import os
import tempfile
import unittest
from types import SimpleNamespace

from app import db
from app.coordinator import insert_strategy_correlation


class PortfolioCorrelationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tempdir.name, "project01.db")
        db.settings = SimpleNamespace(database_path=self.db_path)
        db.init_db()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_correlation_insert(self):
        row_id = insert_strategy_correlation(
            {
                "strategy_a_id": "a",
                "strategy_b_id": "b",
                "run_id": 1,
                "return_correlation": 0.2,
                "drawdown_overlap_score": 0.3,
                "same_day_loss_overlap": 0.1,
                "same_session_overlap": 0.4,
                "same_regime_overlap": 0.5,
            }
        )
        self.assertGreater(row_id, 0)


if __name__ == "__main__":
    unittest.main()
