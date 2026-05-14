use project01::distributed::{job::Job, protocol::Stage};
use project01::engine::{EngineAdapter, PlaceholderEngineAdapter};

#[test]
fn placeholder_result_serializes_with_nullable_strategy_metrics() {
    let job = Job {
        id: 7,
        run_id: Some(11),
        stage: Stage::S1,
        payload: serde_json::json!({"stage":"S1"}),
        attempt_count: 0,
        max_attempts: 3,
    };
    let result = PlaceholderEngineAdapter::execute(&job).unwrap();
    let json = serde_json::to_value(&result).unwrap();
    assert_eq!(json["job_id"], 7);
    assert_eq!(json["fitness"], 1.0);
    assert_eq!(
        json["summary"],
        "placeholder engine adapter executed; no live execution"
    );
    assert_eq!(json["cold_test_used"], false);
    assert!(json.get("strategy_metrics").is_some());
    assert!(json["strategy_metrics"].is_null() || json["strategy_metrics"].is_object());
}
