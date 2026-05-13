from fastapi import APIRouter

from ..health import health_snapshot

router = APIRouter()


@router.get("/health")
def health():
    return health_snapshot()
