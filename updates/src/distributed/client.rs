use anyhow::{Context, Result};
use reqwest::blocking::Client;
use serde_json::json;

use super::{job::Job, protocol::bearer, result::WorkerResult, worker::WorkerMode};
use crate::validation::dataset_ranges::collect_data_profile;

#[derive(Debug, Clone)]
pub struct CoordinatorClient {
    base_url: String,
    token: String,
    http: Client,
}

impl CoordinatorClient {
    pub fn from_env() -> Result<Self> {
        let base_url = std::env::var("PROJECT01_COORDINATOR_URL")
            .unwrap_or_else(|_| "http://127.0.0.1:8080/api".to_string());
        let token = std::env::var("PROJECT01_CLUSTER_TOKEN")
            .context("PROJECT01_CLUSTER_TOKEN is required for worker mode")?;
        Ok(Self {
            base_url,
            token,
            http: Client::new(),
        })
    }

    pub fn register(&self, node: &str, mode: WorkerMode) -> Result<()> {
        let ohlcv = std::env::var("PROJECT01_OHLCV_PATH")
            .unwrap_or_else(|_| "/opt/project01/data/mnq_1m.csv".to_string());
        let bbo = std::env::var("PROJECT01_BBO_PATH")
            .unwrap_or_else(|_| "/opt/project01/data/mnq_bbo_1m.csv".to_string());
        let profile = collect_data_profile(&ohlcv, &bbo)?;
        self.http
            .post(format!("{}/workers/register", self.base_url))
            .header("authorization", bearer(&self.token))
            .json(&json!({
              "node_name": node,
              "mode": mode,
              "capabilities": mode.accepted_stages(),
              "data_profile": profile
            }))
            .send()?
            .error_for_status()?;
        Ok(())
    }

    pub fn heartbeat(&self, node: &str, mode: WorkerMode) -> Result<()> {
        self.http
            .post(format!("{}/workers/heartbeat", self.base_url))
            .header("authorization", bearer(&self.token))
            .json(&json!({"node_name": node, "mode": mode}))
            .send()?
            .error_for_status()?;
        Ok(())
    }

    pub fn claim(&self, node: &str, mode: WorkerMode) -> Result<Option<Job>> {
        let response = self
            .http
            .post(format!("{}/jobs/claim", self.base_url))
            .header("authorization", bearer(&self.token))
            .json(&json!({"node_name": node, "mode": mode, "capabilities": mode.accepted_stages()}))
            .send()?
            .error_for_status()?;
        let value: serde_json::Value = response.json()?;
        if value.get("job").is_none() || value["job"].is_null() {
            return Ok(None);
        }
        Ok(Some(serde_json::from_value(value["job"].clone())?))
    }

    pub fn complete(&self, result: &WorkerResult) -> Result<()> {
        self.http
            .post(format!("{}/jobs/complete", self.base_url))
            .header("authorization", bearer(&self.token))
            .json(result)
            .send()?
            .error_for_status()?;
        Ok(())
    }

    pub fn fail(&self, job_id: i64, error: &str, recoverable: bool) -> Result<()> {
        self.http
            .post(format!("{}/jobs/fail", self.base_url))
            .header("authorization", bearer(&self.token))
            .json(&json!({"job_id": job_id, "error": error, "recoverable": recoverable}))
            .send()?
            .error_for_status()?;
        Ok(())
    }
}
