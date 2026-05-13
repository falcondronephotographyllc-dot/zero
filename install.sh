#!/usr/bin/env bash
set -Eeuo pipefail

DRY_RUN="${PROJECT01_DRY_RUN:-0}"
if [[ "$DRY_RUN" == "1" ]]; then
  PROJECT_ROOT="${PROJECT01_PROJECT_ROOT:-/tmp/project01-dry-run}"
else
  PROJECT_ROOT="${PROJECT01_PROJECT_ROOT:-/opt/project01}"
fi
CONFIG_DIR="$PROJECT_ROOT/config"
STATE_DIR="$PROJECT_ROOT/state"
LOG_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data"
OUTPUT_DIR="$PROJECT_ROOT/output"
BIN_DIR="$PROJECT_ROOT/bin"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NODE_NAME="${PROJECT01_NODE_NAME:-}"
PI_IP=""
MEGATRON_IP=""
OPTIMUS_IP=""
STARSCREAM_IP=""

log(){ printf '\n[PROJECT01:%s] %s\n' "${NODE_NAME:-INSTALL}" "$*"; }
run(){ if [[ "$DRY_RUN" == "1" ]]; then echo "DRY_RUN: $*"; else eval "$@"; fi; }
need_root(){ if [[ "$DRY_RUN" != "1" && "${EUID}" -ne 0 ]]; then echo "Run with sudo: sudo $0"; exit 1; fi; }
ask(){ local prompt="$1" var="$2" default="${3:-}" secret="${4:-0}" value=""; if [[ "$DRY_RUN" == "1" ]]; then value="$default"; elif [[ "$secret" == "1" ]]; then read -r -s -p "$prompt" value; echo; else read -r -p "$prompt" value; fi; value="${value:-$default}"; printf -v "$var" '%s' "$value"; }
install_pkg(){ run "apt-get install -y $*"; }
random_token(){ openssl rand -hex 32 2>/dev/null || python3 -c 'import secrets; print(secrets.token_hex(32))'; }

choose_node(){
  if [[ -z "$NODE_NAME" ]]; then
    ask "Enter this node's name: [STARSCREAM / MEGATRON / OPTIMUS / PI] " NODE_NAME
  fi
  NODE_NAME="$(printf '%s' "$NODE_NAME" | tr '[:lower:]' '[:upper:]')"
  case "$NODE_NAME" in STARSCREAM|MEGATRON|OPTIMUS|PI) ;; *) echo "Invalid node: $NODE_NAME"; exit 1;; esac
}

ensure_dirs(){
  if [[ "$DRY_RUN" == "1" ]]; then
    mkdir -p "$PROJECT_ROOT" "$CONFIG_DIR" "$STATE_DIR" "$LOG_DIR" "$DATA_DIR" "$OUTPUT_DIR" "$BIN_DIR"
    echo "DRY_RUN: mkdir -p '$PROJECT_ROOT' '$CONFIG_DIR' '$STATE_DIR' '$LOG_DIR' '$DATA_DIR' '$OUTPUT_DIR' '$BIN_DIR'"
  else
    run "mkdir -p '$PROJECT_ROOT' '$CONFIG_DIR' '$STATE_DIR' '$LOG_DIR' '$DATA_DIR' '$OUTPUT_DIR' '$BIN_DIR'"
  fi
}

copy_repo(){
  if [[ "$SOURCE_DIR" != "$PROJECT_ROOT" && "$DRY_RUN" != "1" ]]; then
    mkdir -p "$PROJECT_ROOT"
    rsync -a --exclude target --exclude .git "$SOURCE_DIR/" "$PROJECT_ROOT/"
  else
    run "rsync -a --exclude target --exclude .git '$SOURCE_DIR/' '$PROJECT_ROOT/'"
  fi
}

install_tailscale(){
  if ! command -v tailscale >/dev/null 2>&1; then
    run "curl -fsSL https://tailscale.com/install.sh | sh"
  else
    log "Tailscale already installed"
  fi
  tailscale status >/dev/null 2>&1 || log "Tailscale is not logged in yet. Run: sudo tailscale up"
}

install_rust(){
  if ! command -v cargo >/dev/null 2>&1; then
    run "curl https://sh.rustup.rs -sSf | sh -s -- -y"
  else
    log "Rust already installed"
  fi
}

install_ollama(){
  if ! command -v ollama >/dev/null 2>&1; then
    run "curl -fsSL https://ollama.com/install.sh | sh"
  fi
  run "systemctl enable --now ollama || true"
  if [[ -f "$PROJECT_ROOT/ollama/Modelfile.project01-brain" ]]; then
    run "ollama pull llama3.2:3b || true"
    run "ollama create project01-brain -f '$PROJECT_ROOT/ollama/Modelfile.project01-brain' || true"
  fi
}

ask_ips(){
  ask "PI Tailscale IP: " PI_IP "${PI_IP:-100.64.0.1}"
  ask "MEGATRON Tailscale IP: " MEGATRON_IP "${MEGATRON_IP:-100.64.0.2}"
  ask "OPTIMUS Tailscale IP: " OPTIMUS_IP "${OPTIMUS_IP:-100.64.0.3}"
  ask "STARSCREAM Tailscale IP: " STARSCREAM_IP "${STARSCREAM_IP:-100.64.0.4}"
}

role(){ case "$NODE_NAME" in PI) echo control_plane;; MEGATRON) echo llm_heavy_worker;; OPTIMUS) echo dedicated_worker;; STARSCREAM) echo dev_flex_worker;; esac; }
default_mode(){ case "$NODE_NAME" in PI) echo off;; MEGATRON|OPTIMUS) echo full_worker;; STARSCREAM) echo dev_only;; esac; }

write_cluster(){
  local mode="${PROJECT01_WORKER_MODE:-$(default_mode)}"
  if [[ "$NODE_NAME" == "STARSCREAM" ]]; then
    ask "Initial STARSCREAM worker mode [off/dev_only/light_worker/full_worker/burst_worker] default dev_only: " mode "$mode"
  fi
  cat > "$CONFIG_DIR/cluster.toml" <<TOML
[cluster]
pi = "$PI_IP"
starscream = "$STARSCREAM_IP"
megatron = "$MEGATRON_IP"
optimus = "$OPTIMUS_IP"

[node]
name = "$NODE_NAME"
role = "$(role)"
worker_mode = "$mode"

[coordinator]
api_url = "http://$PI_IP:8080/api"

[paths]
root = "$PROJECT_ROOT"
state_dir = "$STATE_DIR"
log_dir = "$LOG_DIR"
data_dir = "$DATA_DIR"
output_dir = "$OUTPUT_DIR"
TOML
}

write_env(){
  local token="${PROJECT01_CLUSTER_TOKEN:-}"
  local telegram_token="" telegram_chat="" openai_key="" openai_enabled="N" openai_budget="5" mode
  mode="${PROJECT01_WORKER_MODE:-$(default_mode)}"
  if [[ "$NODE_NAME" == "PI" ]]; then
    token="${token:-$(random_token)}"
    ask "Telegram bot token [optional]: " telegram_token "" 1
    ask "Telegram chat ID [optional]: " telegram_chat ""
    ask "OpenAI API key [optional, press Enter to skip]: " openai_key "" 1
    ask "Enable OpenAI escalation? [y/N]: " openai_enabled "N"
    ask "OpenAI monthly budget USD [default: 5]: " openai_budget "5"
  else
    ask "PROJECT01 cluster token from PI .env: " token "$token" 1
  fi
  cat > "$CONFIG_DIR/.env" <<ENV
PROJECT01_NODE_NAME=$NODE_NAME
PROJECT01_NODE_ROLE=$(role)
PROJECT01_WORKER_MODE=$mode
PROJECT01_CLUSTER_TOKEN=$token
PROJECT01_COORDINATOR_URL=http://$PI_IP:8080/api
TELEGRAM_BOT_TOKEN=$telegram_token
TELEGRAM_CHAT_ID=$telegram_chat
OPENAI_API_KEY=$openai_key
OPENAI_ENABLED=$openai_enabled
OPENAI_MONTHLY_BUDGET_USD=$openai_budget
OPENAI_DAILY_HARD_LIMIT_USD=0.25
OPENAI_ESCALATION_ONLY=true
OLLAMA_BASE_URL=http://$MEGATRON_IP:11434
OLLAMA_PRIMARY_NODE=MEGATRON
OLLAMA_DEFAULT_MODEL=project01-brain
REDIS_URL=redis://127.0.0.1:6379/0
PROJECT01_DB_PATH=$STATE_DIR/project01.db
ENV
  chmod 600 "$CONFIG_DIR/.env"
}

install_base_packages(){
  run "apt-get update"
  case "$NODE_NAME" in
    PI) install_pkg python3 python3-venv python3-pip redis-server sqlite3 tailscale ufw git curl rsync openssh-client openssh-server ca-certificates ;;
    MEGATRON|OPTIMUS) install_pkg build-essential git curl tailscale rsync openssh-client openssh-server pkg-config libssl-dev ca-certificates ;;
    STARSCREAM) install_pkg build-essential git curl tailscale rsync openssh-client openssh-server pkg-config libssl-dev ca-certificates cmake clang lld ;;
  esac
}

build_components(){
  if [[ "$NODE_NAME" == "PI" ]]; then
    run "python3 -m venv '$PROJECT_ROOT/coordinator/.venv'"
    run "'$PROJECT_ROOT/coordinator/.venv/bin/pip' install -e '$PROJECT_ROOT/coordinator'"
    run "systemctl enable --now redis-server || true"
  else
    install_rust
    run "cd '$PROJECT_ROOT' && cargo build --release"
  fi
  if [[ "$NODE_NAME" == "MEGATRON" ]]; then
    install_ollama
  elif [[ "$NODE_NAME" == "STARSCREAM" ]]; then
    local install_backup="N"
    ask "Install backup Ollama on STARSCREAM? [y/N]: " install_backup "N"
    [[ "$install_backup" =~ ^[Yy]$ ]] && install_ollama
  fi
}

install_units(){
  case "$NODE_NAME" in
    PI)
      run "cp '$PROJECT_ROOT/systemd/project01-coordinator.service' /etc/systemd/system/"
      run "cp '$PROJECT_ROOT/systemd/project01-telegram.service' /etc/systemd/system/"
      run "cp '$PROJECT_ROOT/systemd/project01-health.service' /etc/systemd/system/"
      ;;
    MEGATRON|OPTIMUS|STARSCREAM)
      run "cp '$PROJECT_ROOT/systemd/project01-worker.service' /etc/systemd/system/"
      ;;
  esac
  run "systemctl daemon-reload"
}

validate_data(){
  case "$NODE_NAME" in
    PI) return 0 ;;
    STARSCREAM)
      if [[ -s "$HOME/Desktop/data/mnq_1m.csv" && ! -e "$DATA_DIR/mnq_1m.csv" ]]; then run "ln -s '$HOME/Desktop/data/mnq_1m.csv' '$DATA_DIR/mnq_1m.csv'"; fi
      if [[ -s "$HOME/Desktop/data/mnq_bbo_1m.csv" && ! -e "$DATA_DIR/mnq_bbo_1m.csv" ]]; then run "ln -s '$HOME/Desktop/data/mnq_bbo_1m.csv' '$DATA_DIR/mnq_bbo_1m.csv'"; fi
      ;&
    MEGATRON|OPTIMUS)
      if [[ -x "$PROJECT_ROOT/target/release/project01" ]]; then
        run "'$PROJECT_ROOT/target/release/project01' validate-data --ohlcv '$DATA_DIR/mnq_1m.csv' --bbo '$DATA_DIR/mnq_bbo_1m.csv' || true"
      else
        [[ -s "$DATA_DIR/mnq_1m.csv" ]] && echo "PASS mnq_1m.csv" || echo "MISSING $DATA_DIR/mnq_1m.csv"
        [[ -s "$DATA_DIR/mnq_bbo_1m.csv" ]] && echo "PASS mnq_bbo_1m.csv" || echo "MISSING $DATA_DIR/mnq_bbo_1m.csv"
      fi
      ;;
  esac
}

connectivity_tests(){
  for host in "$PI_IP" "$MEGATRON_IP" "$OPTIMUS_IP" "$STARSCREAM_IP"; do
    [[ -z "$host" ]] && continue
    ping -c 1 -W 2 "$host" >/dev/null 2>&1 && echo "PASS ping $host" || echo "WARN ping failed $host"
  done
}

summary(){
  log "Install summary"
  echo "Node: $NODE_NAME"
  echo "Config: $CONFIG_DIR/cluster.toml"
  echo "Env: $CONFIG_DIR/.env"
  echo "No live execution was installed."
  case "$NODE_NAME" in
    PI) echo "Start services: sudo systemctl enable --now project01-coordinator project01-health project01-telegram" ;;
    MEGATRON|OPTIMUS|STARSCREAM) echo "Start worker: sudo systemctl enable --now project01-worker" ;;
  esac
}

main(){
  need_root
  choose_node
  ensure_dirs
  install_base_packages
  install_tailscale
  copy_repo
  ask_ips
  write_cluster
  write_env
  build_components
  install_units
  validate_data
  connectivity_tests
  summary
}
main "$@"
