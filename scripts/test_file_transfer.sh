#!/usr/bin/env bash
set -Eeuo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 user@host"
  exit 2
fi
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
echo project01 > "$tmp"
scp "$tmp" "$1:/tmp/project01-transfer-test"
ssh "$1" 'test "$(cat /tmp/project01-transfer-test)" = project01 && rm /tmp/project01-transfer-test'
