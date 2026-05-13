#!/usr/bin/env bash
set -Eeuo pipefail
if ! command -v tailscale >/dev/null 2>&1; then
  curl -fsSL https://tailscale.com/install.sh | sh
fi
tailscale status >/dev/null 2>&1 || echo "Run: sudo tailscale up"
