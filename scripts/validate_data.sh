#!/usr/bin/env bash
set -Eeuo pipefail
PROJECT_ROOT="${PROJECT01_PROJECT_ROOT:-/opt/project01}"
"$PROJECT_ROOT/target/release/project01" validate-data \
  --ohlcv "$PROJECT_ROOT/data/mnq_1m.csv" \
  --bbo "$PROJECT_ROOT/data/mnq_bbo_1m.csv"
