#!/usr/bin/env bash
set -Eeuo pipefail
PROJECT_ROOT="${PROJECT01_PROJECT_ROOT:-/opt/project01}"
dest="${1:-$PROJECT_ROOT/output/backups}"
mkdir -p "$dest"
tar -czf "$dest/project01-state-$(date -u +%Y%m%dT%H%M%SZ).tar.gz" -C "$PROJECT_ROOT" state config
