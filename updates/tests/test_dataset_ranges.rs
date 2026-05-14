use std::io::Write;

use project01::validation::dataset_ranges::{
    collect_data_profile, parse_date, validate_dataset_files,
};

#[test]
fn parses_project_dates() {
    assert_eq!(parse_date("2015-02-24").unwrap().to_string(), "2015-02-24");
    assert!(parse_date("not-a-date").is_err());
}

#[test]
fn missing_or_corrupt_data_fails_clearly() {
    assert!(validate_dataset_files("/missing/ohlcv.csv", "/missing/bbo.csv").is_err());

    let dir = tempfile::tempdir().unwrap();
    let good = dir.path().join("good.csv");
    let bad = dir.path().join("bad.csv");
    std::fs::File::create(&good)
        .unwrap()
        .write_all(b"date,open,high,low,close,volume\n2020-01-01,1,2,1,2,10\n")
        .unwrap();
    std::fs::File::create(&bad)
        .unwrap()
        .write_all(b"open,high\n1,2\n")
        .unwrap();
    assert!(validate_dataset_files(good.to_str().unwrap(), bad.to_str().unwrap()).is_err());

    let bbo = dir.path().join("bbo.csv");
    std::fs::File::create(&bbo)
        .unwrap()
        .write_all(b"date,bid,ask\n2020-01-01,1,2\n")
        .unwrap();
    let profile = collect_data_profile(good.to_str().unwrap(), bbo.to_str().unwrap()).unwrap();
    assert!(profile.ohlcv_exists);
    assert!(profile.bbo_exists);
    assert!(profile.ohlcv_size_bytes > 0);
    assert!(!profile.ohlcv_sha256.is_empty());
    assert_eq!(profile.first_timestamp, "2020-01-01");
    assert_eq!(profile.last_timestamp, "2020-01-01");
    assert!(profile.approximate_row_count >= 1);
}
