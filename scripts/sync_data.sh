#!/usr/bin/env bash
set -Eeuo pipefail
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 SOURCE_DIR NODE:/opt/project01/data"
  exit 2
fi
rsync -av --progress "$1"/ "$2"/
