#!/usr/bin/env bash
set -Eeuo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 user@host"
  exit 2
fi

target="$1"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
local_send="$(mktemp)"
local_recv="$(mktemp)"
remote_file="/tmp/project01_transfer_test_${ts}.txt"
payload="project01-transfer-${ts}-${RANDOM}"

cleanup() {
  rm -f "$local_send" "$local_recv"
  ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "rm -f '$remote_file'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

printf '%s\n' "$payload" > "$local_send"

scp -q "$local_send" "${target}:${remote_file}"
scp -q "${target}:${remote_file}" "$local_recv"

if [[ "$(cat "$local_recv")" != "$payload" ]]; then
  echo "FAIL file transfer $target"
  exit 1
fi

ssh -o BatchMode=yes -o ConnectTimeout=5 "$target" "rm -f '$remote_file'" >/dev/null 2>&1 || true
echo "PASS file transfer $target"
