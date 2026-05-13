#!/usr/bin/env bash
set -Eeuo pipefail
for host in "$@"; do
  ping -c 1 -W 2 "$host" >/dev/null && echo "PASS $host" || echo "FAIL $host"
done
