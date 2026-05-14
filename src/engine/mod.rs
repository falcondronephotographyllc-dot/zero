use anyhow::{anyhow, Result};

use crate::distributed::{job::Job, protocol::Stage, result::WorkerResult};

pub mod real_v5_adapter;

pub trait EngineAdapter {
    fn execute(job: &Job) -> Result<WorkerResult>;
}

pub struct PlaceholderEngineAdapter;

impl EngineAdapter for PlaceholderEngineAdapter {
    fn execute(job: &Job) -> Result<WorkerResult> {
        let cold_test_used = matches!(job.stage, Stage::ColdTest);
        Ok(WorkerResult {
            job_id: job.id,
            fitness: if cold_test_used { 0.0 } else { 1.0 },
            summary: "placeholder engine adapter executed; no live execution".to_string(),
            cold_test_used,
            strategy_metrics: None,
        })
    }
}

pub struct RealEngineAdapter;

impl EngineAdapter for RealEngineAdapter {
    fn execute(job: &Job) -> Result<WorkerResult> {
        real_v5_adapter::execute_with_real_v5(job).map_err(|_| {
            anyhow!(
                "PROJECT01_ENGINE_MODE=real but the real V5 adapter is not wired. Set PROJECT01_ENGINE_MODE=placeholder for cluster plumbing tests, or wire the real engine."
            )
        })
    }
}
