#!/usr/bin/env bash
# #580 retry: same 8 arms at the briefed $250 stake (all-in, compounding).
set -euo pipefail
cd "$(dirname "$0")/.."
FT="freqtradeorg/freqtrade:stable"
CFG="/freqtrade/user_data/config/config.sweep250.json"
TIMERANGE="${TIMERANGE:-20260409-20261006}"
FEE="${FEE:-0.0005}"
OUT="sweep/2026-10-06-stake250"
mkdir -p "$OUT"
run() {
  local strat="$1" tf="$2"
  docker run --rm -v "$PWD:/freqtrade/user_data" "$FT" backtesting \
    --config "$CFG" --strategy "$strat" --timeframe "$tf" \
    --timerange "$TIMERANGE" --fee "$FEE" --enable-protections \
    --export trades --cache none \
    >"$OUT/${strat}_${tf}.log" 2>&1 || echo "FAILED ${strat} ${tf} (see log)"
  local newest; newest=$(ls -t backtest_results/*.zip 2>/dev/null | head -1)
  if [[ -n "$newest" ]]; then
    cp "$newest" "$OUT/${strat}_${tf}.zip"
    cp "${newest%.zip}.meta.json" "$OUT/${strat}_${tf}.meta.json" 2>/dev/null || true
  fi
  echo "done: ${strat} ${tf}"
}
for tf in 1h 4h; do
  for strat in TrendFollowingMaxDD SweepEmaCross SweepRsiMeanRev SweepDonchianBreakout; do
    run "$strat" "$tf"
  done
done
python3 scripts/summarize_sweep.py "$OUT" | tee "$OUT/SWEEP_TABLE.md"
