# freqtrade — Hybrid Sleeve (MVP)

Main trading system built on **Freqtrade** using a **Hybrid Sleeve** architecture.

## Current MVP (locked Sept 2026)

| Decision | Choice |
|----------|--------|
| Host | Oracle Cloud Always Free |
| Mode | **Dry-run only** (no live orders yet) |
| Exchange | Binance USDT-M perpetual futures |
| First sleeve | **Trend Following** (Sleeve 2) |
| Pairs | BTC, ETH, SOL, BNB (`*/USDT:USDT`) |
| Success bar | Beat NanoClaw’s ~0 PnL with evidence before going live |

NanoClaw (`krantikaridev/nanoclaw`) is parked. It already proved flat/~0 PnL is possible.

## Repo layout

- `config/config.dryrun.json` — Binance futures dry-run config
- `strategies/TrendFollowing.py` — Sleeve 2 trend strategy (4h)
- `docker-compose.yml` — one-command dry-run on a Linux VM
- `docs/hybrid-sleeve-design-v1.md` — full hybrid design (3 sleeves; only Sleeve 2 implemented now)
- `prompts/` — roadmap + tasks for agents

## Quick start (dry-run)

On the Oracle VM (Docker recommended):

```bash
git clone https://github.com/krantikaridev/freqtrade.git
cd freqtrade
mkdir -p logs
docker compose up -d
docker compose logs -f
```

Backtest (optional, after first candles download):

```bash
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config/config.dryrun.json \
  --timeframes 4h --days 180

docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config/config.dryrun.json \
  --strategy TrendFollowing
```

## Principles

- Risk management first
- Quality over quantity
- No live trading until dry-run expectancy looks better than flat
- Keep operational load low

## Status

Phase 2 scaffold: dry-run config + TrendFollowing strategy ready for Oracle deploy.
