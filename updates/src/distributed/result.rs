use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategyMetricsResult {
    pub strategy_id: String,
    pub avg_daily_profit: f64,
    pub max_intraday_dd: f64,
    pub max_daily_loss: f64,
    pub cold_retention: f64,
    pub mffu_breach_rate: f64,
    pub trade_count: u32,
    pub best_session: String,
    pub best_regime: String,
    pub worker_name: String,
    pub stage: String,
    pub payload_json: serde_json::Value,
    pub result_json: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkerResult {
    pub job_id: i64,
    pub fitness: f64,
    pub summary: String,
    pub cold_test_used: bool,
    pub strategy_metrics: Option<StrategyMetricsResult>,
}
