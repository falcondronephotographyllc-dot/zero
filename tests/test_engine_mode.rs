use project01::distributed::{
    job::Job,
    protocol::Stage,
    worker::{engine_mode_from_env, execute_job, EngineMode, WorkerMode},
};

#[test]
fn engine_mode_default_is_placeholder() {
    std::env::remove_var("PROJECT01_ENGINE_MODE");
    assert_eq!(engine_mode_from_env().unwrap(), EngineMode::Placeholder);
}

#[test]
fn placeholder_mode_executes() {
    std::env::set_var("PROJECT01_ENGINE_MODE", "placeholder");
    let result = execute_job(
        &Job {
            id: 1,
            run_id: Some(1),
            stage: Stage::S1,
            payload: serde_json::json!({}),
            attempt_count: 0,
            max_attempts: 3,
        },
        WorkerMode::FullWorker,
    )
    .unwrap();
    assert_eq!(result.job_id, 1);
}

#[test]
fn real_mode_without_adapter_fails_loudly() {
    std::env::set_var("PROJECT01_ENGINE_MODE", "real");
    let err = execute_job(
        &Job {
            id: 1,
            run_id: Some(1),
            stage: Stage::S1,
            payload: serde_json::json!({}),
            attempt_count: 0,
            max_attempts: 3,
        },
        WorkerMode::FullWorker,
    )
    .unwrap_err();
    assert!(err.to_string().contains("real V5 adapter is not wired"));
}
