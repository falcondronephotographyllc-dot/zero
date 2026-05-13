# PROJECT01 Cluster

PROJECT01 is a private four-node MNQ futures strategy discovery cluster. Its objective is to discover a robust portfolio of MNQ strategies that can collectively target about `$1,000/day` from an MFFU Rapid 50k funded account while preserving strict drawdown control, high cold-test retention, low correlation, and zero preferred rule breaches.

It is research-only: no broker login, order routing, NinjaTrader/Tradovate bridge, or live trading execution is included.

## Roles

- `PI`: control plane, Redis, SQLite, FastAPI coordinator, Telegram MVP, health monitor, result aggregator, no heavy compute.
- `MEGATRON`: main Ollama host, primary heavy worker, preferred for `AI_REVIEW`, `S3`, `COLD_TEST`, and heavy validation.
- `OPTIMUS`: primary dedicated compute worker, always-on `S1`/`S2`/`S3` worker, preferred for stable long compute jobs.
- `STARSCREAM`: dev/flexible worker with optional backup Ollama and modes `off`, `dev_only`, `light_worker`, `full_worker`, `burst_worker`.

## Fitness Objective

PROJECT01 is not trying to find a single moonshot strategy. It prefers multiple lower-drawdown, lower-correlation strategies that combine toward the account-level target. Profit alone must never dominate the score when drawdown, breach rate, or cold-test retention are poor.

Priority order:

1. Survive MFFU rules.
2. Avoid hard drawdown breaches.
3. Keep intraday drawdown low.
4. Keep daily loss low.
5. Maintain high cold-test retention.
6. Avoid train/validation/cold-test decay.
7. Maintain stable daily profit.
8. Prefer reasonable trade frequency.
9. Prefer low correlation with archive winners.
10. Scale toward the `$1,000/day` account-level target.

Single-strategy preferred targets:

- Useful: `> $200/day` per contract.
- Strong: `$200-$400/day` per contract.
- Exceptional: `> $1,000/day` only with excellent drawdown and cold-test behavior.
- Preferred intraday drawdown: `< $800` per contract.
- Cold-test retention: `> 80%`.
- MFFU breach rate: `0%` preferred.

Portfolio targets:

- Combined daily target near `$1,000/day`.
- Low strategy correlation and low same-day/session/regime loss overlap.
- High cold-test retention and stable performance across years.
- Reject or warn when combined drawdown violates account safety.

## Scheduling

- `S1`: `OPTIMUS`, `MEGATRON`, and `STARSCREAM` if available.
- `S2`: `MEGATRON` and `OPTIMUS` preferred; `STARSCREAM` if `light_worker`, `full_worker`, or `burst_worker`.
- `S3`: `MEGATRON` and `OPTIMUS` preferred; `STARSCREAM` only if `full_worker` or `burst_worker`.
- `COLD_TEST`: `MEGATRON` and `OPTIMUS` preferred; `STARSCREAM` only if `full_worker`.
- `AI_REVIEW`: `MEGATRON` Ollama first; `STARSCREAM` Ollama fallback if enabled; OpenAI only when enabled, budget remains, and escalation is justified.

## OpenAI Cost Guard

Ollama/project01-brain handles normal AI work. OpenAI is optional, escalation-only, capped by default at about `$5/month`, and must not run inside the hot strategy evaluation loop.

## After a Device Wipe

Copy the repo or a release archive to the device, then run the matching downloadable wrapper:

```bash
chmod +x dist/setup_pi.sh dist/setup_megatron.sh dist/setup_optimus.sh dist/setup_starscream.sh
sudo dist/setup_pi.sh
sudo dist/setup_megatron.sh
sudo dist/setup_optimus.sh
sudo dist/setup_starscream.sh
```

The wrappers call `install.sh` with the correct node preselected. You can also run `sudo ./install.sh` and choose the node interactively.

## Required Manual Inputs

- Tailscale IPs for `PI`, `MEGATRON`, `OPTIMUS`, and `STARSCREAM`.
- Telegram bot token and chat ID if you want Telegram control.
- OpenAI API key only if you explicitly want optional escalation.
- Cluster token from the PI `/opt/project01/config/.env` when installing workers.
- MNQ data files on each worker at `/opt/project01/data/mnq_1m.csv` and `/opt/project01/data/mnq_bbo_1m.csv`.

## Common Commands

```bash
cargo run --release -- worker --node MEGATRON --mode full_worker
cargo run --release -- worker --node OPTIMUS --mode full_worker
cargo run --release -- worker --node STARSCREAM --mode light_worker
cargo run --release -- validate-data --ohlcv /opt/project01/data/mnq_1m.csv --bbo /opt/project01/data/mnq_bbo_1m.csv
cargo run --release -- local-run --ohlcv /opt/project01/data/mnq_1m.csv --bbo /opt/project01/data/mnq_bbo_1m.csv
```

## API

Base URL: `http://PI_TAILSCALE_IP:8080/api`

All API calls use:

```http
Authorization: Bearer PROJECT01_CLUSTER_TOKEN
```

Portfolio support:

- `GET /api/portfolios/best`
- `POST /api/portfolios/score`

Relevant config examples live in `config/objective.example.toml`, `config/ai.example.toml`, `config/datasets.example.toml`, and `config/walk_forward.example.toml`.

## Limits

This MVP provides the distributed control surface and compatibility wrapper. Strategy search internals are placeholder-safe until the real engine is added behind `src/distributed/worker.rs`.
