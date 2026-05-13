use anyhow::{anyhow, Result};

#[derive(Debug, Clone, Copy)]
pub struct OpenAiBudget {
    pub monthly_limit_usd: f64,
    pub daily_limit_usd: f64,
    pub month_spend_usd: f64,
    pub day_spend_usd: f64,
}

impl OpenAiBudget {
    pub fn can_spend(self, estimate_usd: f64) -> Result<()> {
        if self.month_spend_usd + estimate_usd > self.monthly_limit_usd {
            return Err(anyhow!("OpenAI monthly budget would be exceeded"));
        }
        if self.day_spend_usd + estimate_usd > self.daily_limit_usd {
            return Err(anyhow!("OpenAI daily hard limit would be exceeded"));
        }
        Ok(())
    }
}
