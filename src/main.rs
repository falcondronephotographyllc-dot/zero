use anyhow::Result;
use clap::{Parser, Subcommand};
use project01::distributed::worker::{run_worker, WorkerMode};
use project01::validation::dataset_ranges::validate_dataset_files;

#[derive(Parser)]
#[command(name = "project01")]
#[command(about = "PROJECT01 distributed MNQ strategy discovery engine")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Worker {
        #[arg(long)]
        node: String,
        #[arg(long, default_value = "light_worker")]
        mode: WorkerMode,
    },
    ValidateData {
        #[arg(long)]
        ohlcv: String,
        #[arg(long)]
        bbo: String,
    },
    LocalRun {
        #[arg(long)]
        ohlcv: String,
        #[arg(long)]
        bbo: String,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Worker { node, mode } => run_worker(&node, mode),
        Commands::ValidateData { ohlcv, bbo } => {
            validate_dataset_files(&ohlcv, &bbo)?;
            println!("PASS dataset validation");
            Ok(())
        }
        Commands::LocalRun { ohlcv, bbo } => {
            validate_dataset_files(&ohlcv, &bbo)?;
            println!("PASS local validation run placeholder: no live execution added");
            Ok(())
        }
    }
}
