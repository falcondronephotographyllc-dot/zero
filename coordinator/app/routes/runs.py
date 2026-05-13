from fastapi import APIRouter

from ..coordinator import create_run, current_run, update_run
from ..schemas import RunCreate

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
