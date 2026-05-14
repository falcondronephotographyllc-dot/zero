import unittest
from enum import Enum

from app.models import JobStatus, Stage, WorkerMode


class TestEnums(unittest.TestCase):
    def test_worker_mode_is_enum_compatible_with_py310(self):
        self.assertTrue(issubclass(WorkerMode, Enum))
        self.assertEqual(WorkerMode.full_worker.value, "full_worker")

    def test_stage_and_status_enum_types(self):
        self.assertTrue(issubclass(Stage, Enum))
        self.assertTrue(issubclass(JobStatus, Enum))


if __name__ == "__main__":
    unittest.main()
