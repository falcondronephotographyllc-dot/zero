use anyhow::{anyhow, Result};

use crate::distributed::{job::Job, result::WorkerResult};

// Integration boundary for the existing PROJECT01 V5 engine.
// The real V5 integration must expose:
// - load datasets
// - execute S1 job
// - execute S2 job
// - execute S3 job
// - execute COLD_TEST job
// - return WorkerResult with StrategyMetricsResult
pub fn execute_with_real_v5(_job: &Job) -> Result<WorkerResult> {
    Err(anyhow!(
        "real_v5_adapter boundary exists, but V5 engine files are not wired yet"
    ))
}

pub fn is_real_v5_wired() -> bool {
    false
}
