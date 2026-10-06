# Decision gate replay — last 90 days, with vs without (#580)

Paper only. Replay of the 6 Oct $250-stake sweep exports through
`decision_gate/`: confidence gate (fresh-trend + momentum + regime) then
hard limits (position %, stop, daily cap, max open, kill file), one receipt
row per decision in `receipts/replay/`.

Method: entry-time indicators rebuilt from repo feather candles, no
lookahead. `wait` = next-candle confirmation (1h arms: next candle within
2h). All-in backtest stakes resized to the 100%-equity cap proportionally
so the table compares the confidence filter, not sizing. Run:
`python3 scripts/replay_gate.py --window-days 90 --out receipts/replay --arm <Strategy_TF>`.

## The table (last 90d of the 180d sweep window)

| Arm | Mode | Trades | Win % | Profit $ | Profit % | Max DD % | PF |
|---|---|---|---|---|---|---|---|
| TrendFollowingMaxDD 1h | no-gate | 39 | 87.2 | 43.04 | 17.22 | 17.13 | 1.544 |
| TrendFollowingMaxDD 1h | gate | 33 | 87.9 | 39.33 | 15.73 | 11.99 | 1.700 |
| SweepEmaCross 1h | no-gate | 59 | 62.7 | 89.54 | 35.82 | 14.03 | 1.646 |
| SweepEmaCross 1h | gate | 49 | 57.1 | 35.47 | 14.19 | 14.05 | 1.301 |
| SweepDonchianBreakout 1h | no-gate | 56 | 58.9 | 57.14 | 22.86 | 9.55 | 1.567 |
| SweepDonchianBreakout 1h | gate | 38 | 57.9 | 29.09 | 11.64 | 6.73 | 1.387 |
| TrendFollowingMaxDD 4h | no-gate | 36 | 91.7 | 53.28 | 21.31 | 5.62 | 2.556 |
| TrendFollowingMaxDD 4h | gate | 22 | 90.9 | 34.94 | 13.98 | 5.36 | 2.954 |

## Read

- The gate is selective everywhere (15-32% fewer trades) and lowers
  drawdown on 3 of 4 arms, but it also cuts absolute profit — the skipped
  trades included winners. PF improves on the champ (both TFs), falls on
  the two stock patterns.
- Verdict: the gate is a risk trimmer, not an edge finder. It does what
  the brief asked (fewer, calmer trades with receipts) but does not turn
  a strategy profitable that isn't. No threshold tuning was done on this
  window — that would be overfit.
- Next: dry-run on the Mumbai VM with receipts flowing (7 Oct), then
  compare strategies with Qoder 012's results (8-9 Oct), Gate A review
  package for Madan (10-12 Oct). Going live needs Madan after 7+ days of
  paper passing Gate A.
