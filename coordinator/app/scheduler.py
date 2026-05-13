from __future__ import annotations

from .coordinator import now
from .db import connect


def requeue_stale_jobs() -> int:
    with connect() as db:
        cur = db.execute(
            """
            UPDATE jobs
            SET status='queued', claimed_by=NULL, claimed_at=NULL, attempt_count=attempt_count+1
            WHERE status='claimed' AND attempt_count < max_attempts
            """
        )
        db.execute("INSERT INTO worker_events(node_name, event, created_at) VALUES('PI', 'requeue_stale', ?)", (now(),))
        return cur.rowcount
