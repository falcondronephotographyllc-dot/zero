#!/usr/bin/env bash
set -Eeuo pipefail
if ! command -v cargo >/dev/null 2>&1; then
  curl https://sh.rustup.rs -sSf | sh -s -- -y
fi
