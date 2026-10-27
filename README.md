# freqtrade — Hybrid Sleeve (MVP)

## Live dry-run champ (2026-09-09)

Still **dry-run only**. Current champ on the Oracle host is `TrendFollowingMaxDD` (long-only, BTC/ETH/BNB, max 1 trade, lev 1, $250 wallet). Backtest with protections: **+9.29% / PF 1.27 / DD 9.75%**. Scoreboard: [`docs/ITERATE_SCOREBOARD.md`](docs/ITERATE_SCOREBOARD.md). Config: `config/config.dryrun.micro.nosol.json`.

### Paper pair on the Mac lane (2026-10-27)

Two arms run side by side, **paper money only** — `dry_run: true`, empty `exchange.key` / `exchange.secret`, 250 USDT wallet, 50 USDT stake, `max_open_trades: 1`, BTC/ETH/BNB USDT-M perpetuals, on colima Docker.

| Container | Strategy | Timeframe | Config |
|-----------|----------|-----------|--------|
| `freqtrade-trend-dryrun` | `TrendFollowingMaxDD` (champ) | 4h | `config/config.dryrun.micro.nosol.json` |
| `freqtrade-sweep-ema-dryrun` | `SweepEmaCross` — rank 1 of the 6 Oct $250 stake sweep: +42.93% / Sharpe 1.79 / DD 13.35% over 110 trades vs buy-and-hold +25.08% ([sweep writeup](https://github.com/krantikaridev/freqtrade/blob/air/backtest-sweep-2026-10-06/docs/SWEEP-2026-10-06-STAKE250.md), [freqtrade#9](https://github.com/krantikaridev/freqtrade/pull/9)) | 1h | `config/config.dryrun.sweepema.nosol.json` |

Bring the pair up with `docker compose up -d`, then prove it is alive with `bash scripts/paper_pair_check.sh` — PASS / FAIL / BLOCKED on container state, `dry_run: true`, empty keys and heartbeat age (test: `bash tests/test_paper_pair_check.sh`). Paper-trade DBs and logs are gitignored, and journals go to the `self-data` checkout, not here. No live orders, no keys, no seed capital.


Main trading system built on **Freqtrade** using a **Hybrid Sleeve** architecture.

## Current MVP (locked Sept 2026)

| Decision | Choice |
|----------|--------|
| Host | Oracle Cloud Always Free |
| Mode | **Dry-run only** (no live orders yet) |
| Exchange | Binance USDT-M perpetual futures |
| First sleeve | **Trend Following** (Sleeve 2) — live champ `TrendFollowingMaxDD` (was the `TrendFollowing` scaffold) |
| Pairs | BTC, ETH, BNB (`*/USDT:USDT`) — SOL dropped in the champ |
| Positions | `max_open_trades`: 1 · lev 1 · $250 wallet · 4h |
| Success bar | Beat NanoClaw’s ~0 PnL with evidence before going live |

NanoClaw (`krantikaridev/nanoclaw`) is parked. It already proved flat/~0 PnL is possible.

## Repo layout

- `config/config.dryrun.json` — Binance futures dry-run config
- `strategies/TrendFollowing.py` — Sleeve 2 trend strategy (4h)
- `docker-compose.yml` — one-command dry-run on a Linux VM
- `scripts/paper_pair_check.sh` — one-command proof the Mac paper pair is alive (PASS/FAIL/BLOCKED)
- `docs/hybrid-sleeve-design-v1.md` — full hybrid design (3 sleeves; only Sleeve 2 implemented now)
- `signals/` — Quantral-led watchlist + stuck notes (gather-info, not auto-trade)
- `prompts/` — roadmap + tasks for agents

## Signals

Signal sources and persona notes for the Hybrid Sleeve live in [`signals/`](./signals/). Start with [`signals/WATCHLIST.md`](./signals/WATCHLIST.md). Primary track-record board: [Quantral](https://quantral.com/leaderboard).

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
