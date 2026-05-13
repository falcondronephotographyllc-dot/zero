from __future__ import annotations

from .db import connect


def health_snapshot() -> dict:
    with connect() as db:
        workers = db.execute("SELECT COUNT(*) AS c FROM workers").fetchone()["c"]
        queued = db.execute("SELECT COUNT(*) AS c FROM jobs WHERE status='queued'").fetchone()["c"]
    return {"ok": True, "workers": workers, "queued_jobs": queued}


if __name__ == "__main__":
    print(health_snapshot())
