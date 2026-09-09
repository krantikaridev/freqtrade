# TrendFollowing iterate scoreboard
Window: 2025-04-03 → 2026-09-04 · wallet $250 · lev 1 · 4h futures

| Variant | Profit % | PF | Max DD | Trades | WR | Notes |
|---------|----------|-----|--------|--------|-----|-------|
| Baseline (shorts+SOL+exit) | -15.75% | 0.92 | 23.3% | 909 | 73.6% | original MVP |
| NoExit only | -15.97% | 0.91 | 28.9% | 751 | 82.4% | |
| LongOnly (+SOL) | -4.66% | 0.94 | 19.7% | 368 | 83.7% | |
| LongNoSol (max2) | +5.38% | 1.09 | 11.3% | 287 | 86.1% | prior champ |
| BTC+ETH only | -3.82% | 0.94 | 17.9% | 238 | 84.0% | |
| WideSL -8% | +0.73% | 1.01 | 16.8% | 252 | 88.1% | |
| Soft ROI | -0.99% | 0.98 | 14.0% | 345 | 89.9% | |
| ADX>28 | -10.26% | 0.82 | 18.1% | 223 | 83.0% | |
| EMA 8/21 | +0.99% | 1.01 | 15.5% | 304 | 85.5% | |
| Strict ADX25+vol | -6.60% | 0.89 | 16.0% | 249 | 83.5% | |
| BTC+BNB only | +4.67% | 1.10 | 9.5% | 208 | 87.0% | lower DD |
| Tighter trailing | +5.09% | 1.08 | 11.3% | 292 | 86.3% | |
| LongNoSol max1 | +8.91% | 1.25 | 9.4% | 172 | 87.2% | prior live; BT w/o protections flag |
| ATRStop 2.5x (no trail) | +1.12% | 1.02 | 9.7% | 231 | 74.9% | custom SL; below champ |
| ROI ladder denser | +8.61% | 1.24 | 9.4% | 172 | 86.6% | around champ; below champ |
| **MaxDD tight 8% (champ)** | **+9.29%** | **1.27** | **9.75%** | **167** | **87.4%** | **live dry-run; BT --enable-protections** |

## Fair-compare note (2026-09-09)
LongNoSol max1 with `--enable-protections`: +8.56% / PF 1.24 / DD 9.51% / 170 trades.
MaxDD beat that and the prior scoreboard champ on profit%; DD under 12% gate.

## Live dry-run
- Strategy: `TrendFollowingMaxDD`
- Pairs: BTC/ETH/BNB USDT-M
- `max_open_trades`: 1 · stake 50 · wallet 250 · lev 1 · `use_exit_signal`: false
- MaxDrawdown: lookback 72 / trade_limit 2 / stop 36 / max_allowed_drawdown 0.08
- DB: `tradesv3.dryrun.maxdd.sqlite`

## Gate
Still dry-run. Prefer ≥2–3 days paper journal before any seed. Next iterates: 1h smoke. (ATRStop done 2026-09-07; ROI ladder done 2026-09-08; MaxDD done 2026-09-09)

