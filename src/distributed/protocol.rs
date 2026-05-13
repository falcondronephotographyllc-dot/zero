use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Stage {
    S1,
    S2,
    S3,
    ColdTest,
    AiReview,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum JobStatus {
    Queued,
    Claimed,
    Completed,
    Failed,
    Stale,
}

pub fn bearer(token: &str) -> String {
    format!("Bearer {token}")
}
