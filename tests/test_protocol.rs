use project01::distributed::{protocol::Stage, worker::WorkerMode};

#[test]
fn worker_modes_accept_expected_stages() {
    assert!(!WorkerMode::Off.accepts(Stage::S1));
    assert!(!WorkerMode::DevOnly.accepts(Stage::S1));
    assert!(WorkerMode::LightWorker.accepts(Stage::S1));
    assert!(WorkerMode::LightWorker.accepts(Stage::S2));
    assert!(!WorkerMode::LightWorker.accepts(Stage::S3));
    assert!(WorkerMode::FullWorker.accepts(Stage::ColdTest));
    assert!(WorkerMode::FullWorker.accepts(Stage::AiReview));
    assert!(WorkerMode::BurstWorker.accepts(Stage::S3));
    assert!(!WorkerMode::BurstWorker.accepts(Stage::ColdTest));
}
