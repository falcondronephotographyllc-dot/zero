from fastapi import APIRouter

from ..coordinator import create_run, current_run, generate_jobs_for_run, update_run
from ..schemas import GenerateJobsRequest, RunCreate

router = APIRouter(prefix="/runs")


@router.post("/create")
def create(payload: RunCreate):
    return create_run(payload.name, payload.config)


@router.post("/{run_id}/start")
def start(run_id: int):
    return update_run(run_id, "running")


@router.post("/{run_id}/pause")
def pause(run_id: int):
    return update_run(run_id, "paused")


@router.post("/{run_id}/resume")
def resume(run_id: int):
    return update_run(run_id, "running")


@router.post("/{run_id}/stop_after_current")
def stop_after_current(run_id: int):
    return update_run(run_id, "stop_after_current")


@router.get("/current")
def current():
    return current_run()


@router.get("/{run_id}")
def get_run(run_id: int):
    return {"run_id": run_id}


@router.post("/{run_id}/generate-jobs")
def generate_jobs(run_id: int, payload: GenerateJobsRequest):
    created = generate_jobs_for_run(run_id, payload.model_dump())
    return {"run_id": run_id, "created_jobs": created}
