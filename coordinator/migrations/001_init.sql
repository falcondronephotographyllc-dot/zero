CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  config_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS workers (
  node_name TEXT PRIMARY KEY,
  mode TEXT NOT NULL,
  capabilities_json TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL,
  last_heartbeat TEXT
);

CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER,
  stage TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  priority INTEGER NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL DEFAULT '{}',
  result_json TEXT,
  claimed_by TEXT,
  claimed_at TEXT,
  completed_at TEXT,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 3,
  error TEXT,
  FOREIGN KEY(run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS strategy_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER,
  job_id INTEGER,
  strategy_id TEXT,
  fitness REAL NOT NULL,
  summary TEXT,
  cold_test_used INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS strategy_archives (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  archive_name TEXT NOT NULL,
  path TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS worker_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  node_name TEXT NOT NULL,
  event TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER,
  provider TEXT NOT NULL,
  prompt TEXT,
  response TEXT,
  confidence REAL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_memory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telegram_commands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  command TEXT NOT NULL,
  chat_id TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cost_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT NOT NULL,
  cost_usd REAL NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_candidates (
  portfolio_id TEXT PRIMARY KEY,
  run_id INTEGER,
  strategy_ids_json TEXT NOT NULL,
  combined_avg_daily_profit REAL NOT NULL,
  combined_max_intraday_dd REAL NOT NULL,
  combined_cold_retention REAL NOT NULL,
  combined_breach_rate REAL NOT NULL,
  correlation_score REAL NOT NULL,
  session_overlap_score REAL NOT NULL,
  regime_overlap_score REAL NOT NULL,
  portfolio_fitness REAL NOT NULL,
  warning_flags_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS strategy_correlations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  strategy_a_id TEXT NOT NULL,
  strategy_b_id TEXT NOT NULL,
  run_id INTEGER,
  return_correlation REAL NOT NULL,
  drawdown_overlap_score REAL NOT NULL,
  same_day_loss_overlap REAL NOT NULL,
  same_session_overlap REAL NOT NULL,
  same_regime_overlap REAL NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_stage ON jobs(status, stage);
CREATE INDEX IF NOT EXISTS idx_jobs_run_id ON jobs(run_id);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);
CREATE INDEX IF NOT EXISTS idx_strategy_results_run_id ON strategy_results(run_id);
CREATE INDEX IF NOT EXISTS idx_strategy_results_fitness ON strategy_results(fitness DESC);
CREATE INDEX IF NOT EXISTS idx_ai_decisions_run_id ON ai_decisions(run_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_candidates_run_id ON portfolio_candidates(run_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_candidates_fitness ON portfolio_candidates(portfolio_fitness DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_correlations_pair ON strategy_correlations(strategy_a_id, strategy_b_id);
