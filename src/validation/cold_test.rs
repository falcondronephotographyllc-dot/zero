use anyhow::{anyhow, Result};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Qualification {
    Unqualified,
    QualifiedS3,
}

pub fn ensure_cold_test_allowed(qualification: Qualification) -> Result<()> {
    match qualification {
        Qualification::QualifiedS3 => Ok(()),
        Qualification::Unqualified => {
            Err(anyhow!("cold test is allowed only after S3 qualification"))
        }
    }
}
