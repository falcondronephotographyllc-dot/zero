from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .config import settings
from .coordinator import now
from .db import connect


def requeue_stale_jobs() -> int:
    stale_cutoff = datetime.now(UTC) - timedelta(seconds=settings.heartbeat_stale_seconds)
    stale_cutoff_iso = stale_cutoff.isoformat()
    with connect() as db:
        cur = db.execute(
            """
            UPDATE jobs
            SET status='queued', claimed_by=NULL, claimed_at=NULL, attempt_count=attempt_count+1
            WHERE status='claimed'
              AND attempt_count < max_attempts
              AND (
                claimed_at < ?
                OR claimed_by IN (
                  SELECT node_name FROM workers
                  WHERE last_heartbeat IS NULL OR last_heartbeat < ?
                )
              )
            """
            ,
            (stale_cutoff_iso, stale_cutoff_iso),
        )
        db.execute(
            "INSERT INTO worker_events(node_name, event, created_at) VALUES('PI', 'requeue_stale', ?)",
            (now(),),
        )
        return cur.rowcount
