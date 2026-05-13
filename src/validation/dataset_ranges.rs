use std::{
    fs::File,
    io::{BufRead, BufReader},
};

use anyhow::{anyhow, Context, Result};
use chrono::NaiveDate;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DatasetRange {
    pub start: NaiveDate,
    pub end: NaiveDate,
}

impl DatasetRange {
    pub fn full() -> Self {
        Self {
            start: NaiveDate::from_ymd_opt(2015, 2, 24).unwrap(),
            end: NaiveDate::from_ymd_opt(2026, 3, 24).unwrap(),
        }
    }
}

pub fn parse_date(value: &str) -> Result<NaiveDate> {
    NaiveDate::parse_from_str(value.trim(), "%Y-%m-%d")
        .with_context(|| format!("invalid date: {value}"))
}

pub fn validate_dataset_files(ohlcv_path: &str, bbo_path: &str) -> Result<()> {
    validate_csv_has_dates(ohlcv_path).context("OHLCV dataset failed validation")?;
    validate_csv_has_dates(bbo_path).context("BBO dataset failed validation")?;
    Ok(())
}

fn validate_csv_has_dates(path: &str) -> Result<()> {
    let file = File::open(path).with_context(|| format!("missing data file: {path}"))?;
    let mut lines = BufReader::new(file).lines();
    let header = lines
        .next()
        .transpose()?
        .ok_or_else(|| anyhow!("empty data file: {path}"))?;
    if !header.to_ascii_lowercase().contains("date")
        && !header.to_ascii_lowercase().contains("time")
    {
        return Err(anyhow!("missing date/time column in header: {path}"));
    }
    let first_data = lines
        .find_map(Result::ok)
        .ok_or_else(|| anyhow!("no data rows in file: {path}"))?;
    if first_data.trim().is_empty() {
        return Err(anyhow!("first data row is empty: {path}"));
    }
    Ok(())
}
