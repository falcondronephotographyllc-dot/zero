use project01::validation::cold_test::{ensure_cold_test_allowed, Qualification};

#[test]
fn cold_test_requires_s3_qualification() {
    assert!(ensure_cold_test_allowed(Qualification::Unqualified).is_err());
    assert!(ensure_cold_test_allowed(Qualification::QualifiedS3).is_ok());
}
