from fastapi import APIRouter

from ..ai_bridge import ask_local, ask_openai
from ..schemas import AiQuestion

router = APIRouter(prefix="/ai")


@router.post("/local")
def local(payload: AiQuestion):
    return ask_local(payload.question)


@router.post("/openai")
def openai(payload: AiQuestion):
    return ask_openai(payload.question)


@router.get("/decisions")
def decisions():
    return {"decisions": []}


@router.get("/cost")
def cost():
    return {"monthly_budget_usd": 5, "spent_usd": 0}


@router.get("/working-theory")
def working_theory():
    return {"theory": "Prefer robust walk-forward candidates; cold test remains quarantined."}
