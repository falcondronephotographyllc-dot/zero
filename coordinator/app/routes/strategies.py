from fastapi import APIRouter

from ..aggregator import best_strategies

router = APIRouter(prefix="/strategies")


@router.get("/best")
def best():
    return {"strategies": best_strategies()}


@router.get("/{strategy_id}")
def strategy(strategy_id: str):
    return {"strategy_id": strategy_id}
