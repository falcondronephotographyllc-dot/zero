use project01::validation::{dataset_ranges::parse_date, walk_forward::WalkForward};

#[test]
fn cold_period_is_excluded_from_training() {
    let wf = WalkForward::project_default();
    wf.validate().unwrap();
    assert!(wf.is_training_date(parse_date("2020-12-31").unwrap()));
    assert!(!wf.is_training_date(parse_date("2024-01-01").unwrap()));
}

#[test]
fn validation_period_is_separate_from_training() {
    let wf = WalkForward::project_default();
    assert!(wf.is_validation_date(parse_date("2021-01-01").unwrap()));
    assert!(!wf.is_training_date(parse_date("2021-01-01").unwrap()));
}
