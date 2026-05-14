from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException

from .config import settings
from .db import init_db
from .routes import ai, archives, health, jobs, portfolios, runs, strategies, workers

app = FastAPI(title="PROJECT01 Coordinator", version="0.1.0")


def require_auth(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {settings.cluster_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="invalid cluster token")


@app.on_event("startup")
def startup() -> None:
    if settings.cluster_token == "dev-token" and not settings.allow_dev_token:
        raise RuntimeError("PROJECT01_CLUSTER_TOKEN=dev-token is not allowed outside dev mode")
    init_db()


app.include_router(health.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(workers.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(jobs.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(runs.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(strategies.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(portfolios.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(archives.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(ai.router, prefix="/api", dependencies=[Depends(require_auth)])


@app.get("/")
def root():
    return {"name": "PROJECT01", "live_execution": False}
