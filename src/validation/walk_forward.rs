use anyhow::{anyhow, Result};
use chrono::NaiveDate;

use super::dataset_ranges::parse_date;

#[derive(Debug, Clone)]
pub struct WalkForward {
    pub train_start: NaiveDate,
    pub train_end: NaiveDate,
    pub validation_start: NaiveDate,
    pub validation_end: NaiveDate,
    pub cold_start: NaiveDate,
    pub cold_end: NaiveDate,
}

impl WalkForward {
    pub fn project_default() -> Self {
        Self {
            train_start: parse_date("2015-02-24").unwrap(),
            train_end: parse_date("2020-12-31").unwrap(),
            validation_start: parse_date("2021-01-01").unwrap(),
            validation_end: parse_date("2023-12-31").unwrap(),
            cold_start: parse_date("2024-01-01").unwrap(),
            cold_end: parse_date("2026-03-24").unwrap(),
        }
    }

    pub fn validate(&self) -> Result<()> {
        if self.train_end >= self.validation_start {
            return Err(anyhow!("training overlaps validation"));
        }
        if self.validation_end >= self.cold_start {
            return Err(anyhow!("validation overlaps cold test"));
        }
        Ok(())
    }

    pub fn is_training_date(&self, date: NaiveDate) -> bool {
        date >= self.train_start && date <= self.train_end
    }

    pub fn is_validation_date(&self, date: NaiveDate) -> bool {
        date >= self.validation_start && date <= self.validation_end
    }

    pub fn is_cold_date(&self, date: NaiveDate) -> bool {
        date >= self.cold_start && date <= self.cold_end
    }
}
