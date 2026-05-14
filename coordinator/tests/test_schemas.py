from app.schemas import JobComplete


def test_job_complete_allows_null_strategy_metrics():
    payload = JobComplete.model_validate(
        {
            "job_id": 1,
            "fitness": 1.0,
            "summary": "placeholder",
            "cold_test_used": False,
            "strategy_metrics": None,
        }
    )
    assert payload.strategy_metrics is None
