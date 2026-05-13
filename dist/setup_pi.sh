#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PROJECT01_NODE_NAME=PI exec ./install.sh
