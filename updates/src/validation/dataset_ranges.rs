use std::{
    fs,
    fs::File,
    io::{BufRead, BufReader, Read},
};

use anyhow::{anyhow, Context, Result};
use chrono::NaiveDate;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

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
    let _ = collect_data_profile(ohlcv_path, bbo_path)?;
    Ok(())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SingleFileProfile {
    pub exists: bool,
    pub size_bytes: u64,
    pub sha256: String,
    pub first_timestamp: String,
    pub last_timestamp: String,
    pub approximate_row_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataProfile {
    pub ohlcv_exists: bool,
    pub bbo_exists: bool,
    pub ohlcv_size_bytes: u64,
    pub bbo_size_bytes: u64,
    pub ohlcv_sha256: String,
    pub bbo_sha256: String,
    pub first_timestamp: String,
    pub last_timestamp: String,
    pub approximate_row_count: u64,
}

pub fn collect_data_profile(ohlcv_path: &str, bbo_path: &str) -> Result<DataProfile> {
    let ohlcv = validate_csv_has_dates(ohlcv_path).context("OHLCV dataset failed validation")?;
    let bbo = validate_csv_has_dates(bbo_path).context("BBO dataset failed validation")?;
    Ok(DataProfile {
        ohlcv_exists: ohlcv.exists,
        bbo_exists: bbo.exists,
        ohlcv_size_bytes: ohlcv.size_bytes,
        bbo_size_bytes: bbo.size_bytes,
        ohlcv_sha256: ohlcv.sha256,
        bbo_sha256: bbo.sha256,
        first_timestamp: ohlcv.first_timestamp,
        last_timestamp: ohlcv.last_timestamp,
        approximate_row_count: ohlcv.approximate_row_count,
    })
}

fn validate_csv_has_dates(path: &str) -> Result<SingleFileProfile> {
    let metadata = fs::metadata(path).with_context(|| format!("missing data file: {path}"))?;
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
    let mut row_count = 0_u64;
    let mut first_data = String::new();
    let mut last_data = String::new();
    for line in lines.map_while(Result::ok) {
        if line.trim().is_empty() {
            continue;
        }
        row_count += 1;
        if first_data.is_empty() {
            first_data = line.clone();
        }
        last_data = line;
    }
    if first_data.is_empty() {
        return Err(anyhow!("no data rows in file: {path}"));
    }
    if first_data.trim().is_empty() {
        return Err(anyhow!("first data row is empty: {path}"));
    }
    let first_timestamp = first_data
        .split(',')
        .next()
        .unwrap_or("")
        .trim()
        .to_string();
    let last_timestamp = last_data.split(',').next().unwrap_or("").trim().to_string();
    if first_timestamp.is_empty() || last_timestamp.is_empty() {
        return Err(anyhow!("missing timestamps in data rows: {path}"));
    }
    let mut file_for_hash =
        File::open(path).with_context(|| format!("missing data file: {path}"))?;
    let mut hasher = Sha256::new();
    let mut buf = [0_u8; 8192];
    loop {
        let read = file_for_hash.read(&mut buf)?;
        if read == 0 {
            break;
        }
        hasher.update(&buf[..read]);
    }
    let sha256 = format!("{:x}", hasher.finalize());
    Ok(SingleFileProfile {
        exists: true,
        size_bytes: metadata.len(),
        sha256,
        first_timestamp,
        last_timestamp,
        approximate_row_count: row_count,
    })
}
