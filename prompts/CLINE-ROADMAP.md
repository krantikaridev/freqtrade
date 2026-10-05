# Cline Roadmap — freqtrade (next 3 slices)

Issue self#131. **Dry-run / paper only.** No live orders, no live keys, no
NanoClaw wallet. Cline may edit docs/config/strategy and run dry-run/backtests;
it may **not** deploy, restart, or pull from the Oracle host — an agent on the
host reads its own journal and appends the scoreboard row.

Source of truth: champ `TrendFollowingMaxDD`, `config/config.dryrun.micro.nosol.json`
(BTC/ETH/BNB, max_open_trades 1, lev 1, $250 wallet), `docs/ITERATE_SCOREBOARD.md`.

## Slice 1 — Scoreboard row for the last dry-run week
- Append one row to `docs/ITERATE_SCOREBOARD.md` for the most recent full dry-run
  week (Mon–Sun) of `TrendFollowingMaxDD` on the Oracle host.
- Read-only metrics from the dry-run journal / `tradesv3.dryrun.maxdd.sqlite`:
  profit %, PF, max DD, trades, WR. Keep the backtest scoreboard separate — label
  this block "Live dry-run weekly".
- If the journal is not reachable (no host access this lane), record
  `BLOCKED — need Oracle journal read` here and in the issue; do not invent a row.
- Still dry-run only. Do not promote anything to live.

## Slice 2 — Sleeve-2 guardrail test
- Verify the `TrendFollowingMaxDD` protections actually trip in dry-run, not just
  in backtest: MaxDrawdown (lookback 72 / trade_limit 2 / stop 36 /
  max_allowed_drawdown 0.08) and the `lev = min(1.0, max_leverage)` clamp.
- Add a small test or checklist that shows (a) DD>8% halts new entries, (b) only one
  position opens at a time, (c) leverage never exceeds 1.
- Report PASS/FAIL per guardrail in the PR. No live trading, no config change that
  raises leverage or opens more than one trade.

## Slice 3 — No live keys (standing guard)
- Keep `exchange.key` / `exchange.secret` empty in every committed config.
- Add a pre-commit / CI check (or repo hook) that fails if any committed config
  contains a non-empty API key/secret or flips `dry_run` to `false`.
- Never touch the NanoClaw wallet. Live capital is a Madan-only decision after the
  dry-run expectancy beats NanoClaw's ~0 PnL with evidence.

## Not on this roadmap
- No live deployment. No seed capital. No leverage > 1. No max_open_trades > 1.
- No new sleeve until Slices 1–3 are green and Madan signs off.
