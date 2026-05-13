use std::{fmt, str::FromStr, thread, time::Duration};

use anyhow::{anyhow, Result};
use clap::ValueEnum;
use serde::{Deserialize, Serialize};

use super::{
    client::CoordinatorClient, heartbeat::HEARTBEAT_INTERVAL_SECONDS, job::Job, protocol::Stage,
    result::WorkerResult,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, ValueEnum)]
#[serde(rename_all = "snake_case")]
pub enum WorkerMode {
    Off,
    DevOnly,
    LightWorker,
    FullWorker,
    BurstWorker,
}

impl WorkerMode {
    pub fn accepts(self, stage: Stage) -> bool {
        match self {
            WorkerMode::Off | WorkerMode::DevOnly => false,
            WorkerMode::LightWorker => matches!(stage, Stage::S1 | Stage::S2),
            WorkerMode::FullWorker => matches!(
                stage,
                Stage::S1 | Stage::S2 | Stage::S3 | Stage::ColdTest | Stage::AiReview
            ),
            WorkerMode::BurstWorker => {
                matches!(stage, Stage::S1 | Stage::S2 | Stage::S3 | Stage::AiReview)
            }
        }
    }

    pub fn accepted_stages(self) -> Vec<&'static str> {
        [
            Stage::S1,
            Stage::S2,
            Stage::S3,
            Stage::ColdTest,
            Stage::AiReview,
        ]
        .into_iter()
        .filter(|stage| self.accepts(*stage))
        .map(|stage| match stage {
            Stage::S1 => "S1",
            Stage::S2 => "S2",
            Stage::S3 => "S3",
            Stage::ColdTest => "COLD_TEST",
            Stage::AiReview => "AI_REVIEW",
        })
        .collect()
    }
}

impl fmt::Display for WorkerMode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let value = match self {
            WorkerMode::Off => "off",
            WorkerMode::DevOnly => "dev_only",
            WorkerMode::LightWorker => "light_worker",
            WorkerMode::FullWorker => "full_worker",
            WorkerMode::BurstWorker => "burst_worker",
        };
        f.write_str(value)
    }
}

impl FromStr for WorkerMode {
    type Err = anyhow::Error;

    fn from_str(value: &str) -> Result<Self> {
        match value {
            "off" => Ok(Self::Off),
            "dev_only" => Ok(Self::DevOnly),
            "light_worker" => Ok(Self::LightWorker),
            "full_worker" => Ok(Self::FullWorker),
            "burst_worker" => Ok(Self::BurstWorker),
            _ => Err(anyhow!("invalid worker mode: {value}")),
        }
    }
}

pub fn run_worker(node: &str, mode: WorkerMode) -> Result<()> {
    if matches!(mode, WorkerMode::Off | WorkerMode::DevOnly) {
        println!("{node} is in {mode}; no queue jobs will be claimed");
        return Ok(());
    }

    let client = CoordinatorClient::from_env()?;
    client.register(node, mode)?;
    loop {
        client.heartbeat(node, mode)?;
        if let Some(job) = client.claim(node, mode)? {
            match execute_job(&job, mode) {
                Ok(result) => client.complete(&result)?,
                Err(error) => client.fail(job.id, &error.to_string(), true)?,
            }
        }
        thread::sleep(Duration::from_secs(HEARTBEAT_INTERVAL_SECONDS));
    }
}

pub fn execute_job(job: &Job, mode: WorkerMode) -> Result<WorkerResult> {
    if !mode.accepts(job.stage) {
        return Err(anyhow!("mode {mode} cannot execute stage {:?}", job.stage));
    }
    let cold_test_used = matches!(job.stage, Stage::ColdTest);
    Ok(WorkerResult {
        job_id: job.id,
        fitness: if cold_test_used { 0.0 } else { 1.0 },
        summary: "placeholder engine wrapper completed safely; no live execution".to_string(),
        cold_test_used,
    })
}
