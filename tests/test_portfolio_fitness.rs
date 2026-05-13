use project01::portfolio::{score_portfolio, PortfolioMetrics};

#[test]
fn portfolio_prefers_diversified_safe_target() {
    let safe = PortfolioMetrics {
        combined_avg_daily_profit: 950.0,
        combined_max_intraday_drawdown: 650.0,
        combined_cold_retention: 0.88,
        combined_breach_rate: 0.0,
        correlation_score: 0.20,
        session_overlap_score: 0.25,
        regime_overlap_score: 0.30,
        same_day_loss_overlap: 0.15,
        year_stability_score: 0.80,
    };
    let concentrated = PortfolioMetrics {
        combined_avg_daily_profit: 1_400.0,
        combined_max_intraday_drawdown: 1_200.0,
        combined_cold_retention: 0.72,
        combined_breach_rate: 0.01,
        correlation_score: 0.90,
        session_overlap_score: 0.90,
        regime_overlap_score: 0.80,
        same_day_loss_overlap: 0.75,
        year_stability_score: 0.30,
    };

    let safe_score = score_portfolio(&safe);
    let concentrated_score = score_portfolio(&concentrated);

    assert!(!safe_score.rejected);
    assert!(concentrated_score.rejected);
    assert!(safe_score.fitness > concentrated_score.fitness);
}
