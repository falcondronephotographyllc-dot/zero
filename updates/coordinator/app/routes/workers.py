from fastapi import APIRouter

from ..coordinator import heartbeat, register_worker, set_worker_mode
from ..schemas import Heartbeat, ModeChange, WorkerRegister

router = APIRouter(prefix="/workers")


@router.post("/register")
def register(payload: WorkerRegister):
    return register_worker(
        payload.node_name,
        payload.mode,
        payload.capabilities,
        payload.data_profile.model_dump(),
    )


@router.post("/heartbeat")
def worker_heartbeat(payload: Heartbeat):
    return heartbeat(payload.node_name, payload.mode)


@router.post("/{node_name}/mode")
def mode(node_name: str, payload: ModeChange):
    return set_worker_mode(node_name, payload.mode)
