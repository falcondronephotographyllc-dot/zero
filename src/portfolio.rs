use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StrategyMetrics {
    pub strategy_id: String,
    pub avg_daily_profit: f64,
    pub max_intraday_drawdown: f64,
    pub daily_loss: f64,
    pub cold_retention: f64,
    pub mffu_breach_rate: f64,
    pub trade_count: u32,
    pub validation_decay: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioMetrics {
    pub combined_avg_daily_profit: f64,
    pub combined_max_intraday_drawdown: f64,
    pub combined_cold_retention: f64,
    pub combined_breach_rate: f64,
    pub correlation_score: f64,
    pub session_overlap_score: f64,
    pub regime_overlap_score: f64,
    pub same_day_loss_overlap: f64,
    pub year_stability_score: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PortfolioScore {
    pub fitness: f64,
    pub rejected: bool,
    pub warning_flags: Vec<String>,
}

pub const ACCOUNT_DAILY_TARGET: f64 = 1_000.0;
pub const STRONG_STRATEGY_DAILY_PROFIT_HIGH: f64 = 400.0;
pub const PREFERRED_INTRADAY_DRAWDOWN: f64 = 800.0;
pub const MIN_COLD_RETENTION: f64 = 0.80;

pub fn score_strategy(metrics: &StrategyMetrics) -> f64 {
    if metrics.mffu_breach_rate > 0.0 {
        return -1_000.0 - metrics.mffu_breach_rate * 10_000.0;
    }

    let profit_score =
        (metrics.avg_daily_profit / STRONG_STRATEGY_DAILY_PROFIT_HIGH).min(1.0) * 15.0;
    let drawdown_score =
        (1.0 - (metrics.max_intraday_drawdown / PREFERRED_INTRADAY_DRAWDOWN).min(1.5)).max(-0.5)
            * 25.0;
    let daily_loss_score =
        (1.0 - (metrics.daily_loss / PREFERRED_INTRADAY_DRAWDOWN).min(1.5)).max(-0.5) * 15.0;
    let cold_score = (metrics.cold_retention / MIN_COLD_RETENTION).min(1.25) * 20.0;
    let decay_score = (1.0 - metrics.validation_decay.min(1.0)).max(0.0) * 15.0;
    let trade_score = if metrics.trade_count >= 20 {
        10.0
    } else {
        -10.0
    };

    drawdown_score + daily_loss_score + cold_score + decay_score + profit_score + trade_score
}

pub fn score_portfolio(metrics: &PortfolioMetrics) -> PortfolioScore {
    let mut warnings = Vec::new();
    let mut rejected = false;

    if metrics.combined_breach_rate > 0.0 {
        warnings.push("mffu_breach".to_string());
        rejected = true;
    }
    if metrics.combined_max_intraday_drawdown > PREFERRED_INTRADAY_DRAWDOWN {
        warnings.push("combined_drawdown_over_safety".to_string());
    }
    if metrics.combined_cold_retention < MIN_COLD_RETENTION {
        warnings.push("cold_retention_below_80pct".to_string());
        rejected = true;
    }
    if metrics.same_day_loss_overlap > 0.50 {
        warnings.push("same_day_loss_overlap".to_string());
    }
    if metrics.session_overlap_score > 0.70 {
        warnings.push("session_concentration".to_string());
    }
    if metrics.regime_overlap_score > 0.70 {
        warnings.push("regime_concentration".to_string());
    }

    let target_score = (1.0
        - ((ACCOUNT_DAILY_TARGET - metrics.combined_avg_daily_profit).abs()
            / ACCOUNT_DAILY_TARGET))
        .clamp(0.0, 1.0)
        * 20.0;
    let drawdown_score = (1.0
        - (metrics.combined_max_intraday_drawdown / PREFERRED_INTRADAY_DRAWDOWN).min(2.0))
    .max(-1.0)
        * 25.0;
    let cold_score = (metrics.combined_cold_retention / MIN_COLD_RETENTION).min(1.25) * 20.0;
    let breach_score = if metrics.combined_breach_rate == 0.0 {
        20.0
    } else {
        -100.0
    };
    let overlap_average = (metrics.correlation_score
        + metrics.session_overlap_score
        + metrics.regime_overlap_score
        + metrics.same_day_loss_overlap)
        / 4.0;
    let diversification_score = (1.0 - overlap_average.min(1.0)) * 25.0;
    let stability_score = metrics.year_stability_score.clamp(0.0, 1.0) * 10.0;

    let mut fitness = target_score
        + drawdown_score
        + cold_score
        + breach_score
        + diversification_score
        + stability_score;
    if rejected {
        fitness -= 1_000.0;
    }

    PortfolioScore {
        fitness,
        rejected,
        warning_flags: warnings,
    }
}
