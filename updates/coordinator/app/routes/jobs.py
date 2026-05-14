from fastapi import APIRouter

from ..job_queue import claim_job, complete_job, fail_job
from ..schemas import JobClaim, JobComplete, JobFail

router = APIRouter(prefix="/jobs")


@router.post("/claim")
def claim(payload: JobClaim):
    return claim_job(payload.node_name, payload.mode)


@router.post("/complete")
def complete(payload: JobComplete):
    return complete_job(
        payload.job_id,
        payload.fitness,
        payload.summary,
        payload.cold_test_used,
        payload.strategy_metrics,
    )


@router.post("/fail")
def fail(payload: JobFail):
    return fail_job(payload.job_id, payload.error, payload.recoverable)
