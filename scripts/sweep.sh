#!/usr/bin/env bash
# Parallel backtest sweep for #580 (6 Oct): champ + 3 stock strategies x 1h/4h.
# Same wallet ($250), stake ($50), max_open_trades 1, fee (0.05% taker),
# pairs (BTC/ETH/BNB USDT-M), window for every arm.
set -euo pipefail

cd "$(dirname "$0")/.."
FT="freqtradeorg/freqtrade:stable"
CFG="/freqtrade/user_data/config/config.sweep.json"
TIMERANGE="${TIMERANGE:-20260409-20261006}"
FEE="${FEE:-0.0005}"
OUT="sweep/2026-10-06"
mkdir -p "$OUT"

run() {
  local strat="$1" tf="$2"
  local before after
  before=$(ls backtest_results 2>/dev/null | sort)
  docker run --rm -v "$PWD:/freqtrade/user_data" "$FT" backtesting \
    --config "$CFG" --strategy "$strat" --timeframe "$tf" \
    --timerange "$TIMERANGE" --fee "$FEE" --enable-protections \
    --export trades \
    >"$OUT/${strat}_${tf}.log" 2>&1 || echo "FAILED ${strat} ${tf} (see log)"
  # freqtrade writes timestamped exports; keep the newest one under the arm name
  after=$(ls backtest_results 2>/dev/null | sort)
  local newest
  newest=$(ls -t backtest_results/*.zip 2>/dev/null | head -1)
  if [[ -n "$newest" && "$after" != "$before" ]]; then
    cp "$newest" "$OUT/${strat}_${tf}.zip"
    cp "${newest%.zip}.meta.json" "$OUT/${strat}_${tf}.meta.json" 2>/dev/null || true
  fi
  echo "done: ${strat} ${tf}"
}

if [[ "${SKIP_DOWNLOAD:-0}" != "1" ]]; then
  docker run --rm -v "$PWD:/freqtrade/user_data" "$FT" download-data \
    --config "$CFG" --timeframes 1h 4h --days 240 --trading-mode futures
fi

for tf in 4h 1h; do
  for strat in TrendFollowingMaxDD SweepEmaCross SweepRsiMeanRev SweepDonchianBreakout; do
    run "$strat" "$tf"
  done
done

python3 scripts/summarize_sweep.py "$OUT"
