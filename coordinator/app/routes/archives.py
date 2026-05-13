from fastapi import APIRouter

router = APIRouter(prefix="/archives")


@router.get("/{archive_name}")
def archive(archive_name: str):
    return {"archive_name": archive_name, "available": False}
