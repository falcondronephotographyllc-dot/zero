use serde::{Deserialize, Serialize};

use super::protocol::Stage;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Job {
    pub id: i64,
    pub run_id: Option<i64>,
    pub stage: Stage,
    pub payload: serde_json::Value,
    pub attempt_count: u32,
    pub max_attempts: u32,
}
