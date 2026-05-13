pub fn summarize_result(strategy_id: &str, fitness: f64) -> String {
    format!("strategy={strategy_id} fitness={fitness:.4}")
}

pub fn summarize_portfolio(portfolio_id: &str, fitness: f64, warnings: &[String]) -> String {
    format!(
        "portfolio={portfolio_id} fitness={fitness:.4} warnings={}",
        warnings.join(",")
    )
}
