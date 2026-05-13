#!/usr/bin/env bash
set -Eeuo pipefail
cp /opt/project01/systemd/project01-worker.service /etc/systemd/system/
systemctl daemon-reload
