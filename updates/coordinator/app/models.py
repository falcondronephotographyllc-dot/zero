from __future__ import annotations

from enum import Enum


class WorkerMode(str, Enum):
    off = "off"
    dev_only = "dev_only"
    light_worker = "light_worker"
    full_worker = "full_worker"
    burst_worker = "burst_worker"


class Stage(str, Enum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    COLD_TEST = "COLD_TEST"
    AI_REVIEW = "AI_REVIEW"


class JobStatus(str, Enum):
    queued = "queued"
    claimed = "claimed"
    completed = "completed"
    failed = "failed"
    stale = "stale"
