#!/usr/bin/env bash
set -Eeuo pipefail
if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
systemctl enable --now ollama || true
ollama pull llama3.2:3b || true
ollama create project01-brain -f /opt/project01/ollama/Modelfile.project01-brain || true
