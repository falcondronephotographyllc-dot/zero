from fastapi import APIRouter

from ..ai_bridge import ask_local, ask_openai
from ..db import connect
from ..config import settings
from ..schemas import AiQuestion

router = APIRouter(prefix="/ai")


@router.post("/local")
def local(payload: AiQuestion):
    return ask_local(payload.question)


@router.post("/openai")
def openai(payload: AiQuestion):
    return ask_openai(payload.question, payload.escalation_reason, payload.explicit_escalation)


@router.get("/decisions")
def decisions():
    return {"decisions": []}


@router.get("/cost")
def cost():
    with connect() as db:
        row = db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) AS spent FROM cost_usage WHERE provider='openai'"
        ).fetchone()
    return {"monthly_budget_usd": settings.openai_monthly_budget_usd, "spent_usd": float(row["spent"])}


@router.get("/working-theory")
def working_theory():
    return {"theory": "Prefer robust walk-forward candidates; cold test remains quarantined."}
