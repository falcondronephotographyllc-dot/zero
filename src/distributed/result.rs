use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkerResult {
    pub job_id: i64,
    pub fitness: f64,
    pub summary: String,
    pub cold_test_used: bool,
}
