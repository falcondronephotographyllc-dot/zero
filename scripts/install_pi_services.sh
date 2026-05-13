#!/usr/bin/env bash
set -Eeuo pipefail
cp /opt/project01/systemd/project01-coordinator.service /etc/systemd/system/
cp /opt/project01/systemd/project01-telegram.service /etc/systemd/system/
cp /opt/project01/systemd/project01-health.service /etc/systemd/system/
systemctl daemon-reload
