#!/usr/bin/env bash
# scripts/paper_pair_check.sh — prove the two dry-run paper bots are alive (self#2071).
# PASS(0): both arms running, dry_run:true, empty keys, heartbeat within STALE_MIN.
# FAIL(1): any arm missing, stopped, stale, or not dry-run.
# BLOCKED(2): docker/python3 absent or daemon unreachable — never a silent PASS.
set -uo pipefail

DOCKER="${DOCKER:-docker}"
PAPER_ROOT="${PAPER_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STALE_MIN="${STALE_MIN:-10}"

# name|config|host log|host sqlite db
ARMS=(
  "freqtrade-trend-dryrun|config/config.dryrun.micro.nosol.json|logs/freqtrade-maxdd.log|tradesv3.dryrun.maxdd.sqlite"
  "freqtrade-sweep-ema-dryrun|config/config.dryrun.sweepema.nosol.json|logs/freqtrade-sweepema.log|tradesv3.dryrun.sweepema.sqlite"
)

command -v "$DOCKER" >/dev/null 2>&1 || { echo "BLOCKED: docker binary not found (DOCKER=$DOCKER)"; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "BLOCKED: python3 not found"; exit 2; }
"$DOCKER" info >/dev/null 2>&1 || { echo "BLOCKED: docker daemon unreachable"; exit 2; }

fail=0
for arm in "${ARMS[@]}"; do
  IFS='|' read -r name cfg logf dbfile <<< "$arm"

  state="$("$DOCKER" inspect -f '{{.State.Status}}' "$name" 2>/dev/null)" || state="missing"
  [ "$state" = "running" ] || { echo "FAIL: $name state='${state:-missing}' (expected running)"; fail=1; }

  safety="$(python3 - "$PAPER_ROOT/$cfg" <<'PY'
import json, sys
try:
    c = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"UNREADABLE {e}"); raise SystemExit
ex = c.get("exchange", {})
if c.get("dry_run") is not True:
    print("UNSAFE dry_run not true")
elif ex.get("key") or ex.get("secret"):
    print("UNSAFE live key or secret present")
else:
    print("SAFE")
PY
)"
  [ "$safety" = "SAFE" ] || { echo "FAIL: $name config $cfg -> $safety"; fail=1; }

  # Container clocks run UTC, so log timestamps compare directly against UTC now.
  hb_line="$(grep 'Bot heartbeat' "$PAPER_ROOT/$logf" 2>/dev/null | tail -1)"
  hb_ts="$(printf '%s' "$hb_line" | awk '{print $1"T"$2}' | cut -d, -f1)"
  age="$(python3 -c "
import sys, datetime
if not sys.argv[1]:
    print('NA'); raise SystemExit
t = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
print(int((datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() // 60))
" "$hb_ts" 2>/dev/null)"
  if [ -z "${age:-}" ] || [ "$age" = "NA" ]; then
    echo "FAIL: $name no heartbeat line in $logf"; fail=1
  elif [ "$age" -gt "$STALE_MIN" ]; then
    echo "FAIL: $name heartbeat ${age}min old (> ${STALE_MIN}min), last '$hb_ts'"; fail=1
  else
    echo "PASS: $name running, dry_run+empty keys OK, heartbeat ${age}min old"
  fi

  opens="$(python3 -c "
import sys, sqlite3
try:
    db = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True)
    print(db.execute('select count(*) from trades where is_open=1').fetchone()[0])
except Exception:
    print('NA')
" "$PAPER_ROOT/$dbfile" 2>/dev/null)"
  echo "  evidence: $name open paper trades=$opens (db $dbfile)"
done

[ "$fail" -eq 0 ] && { echo "PAPER-PAIR: PASS (both arms dry-run, keys empty, heartbeat < ${STALE_MIN}min)"; exit 0; }
echo "PAPER-PAIR: FAIL"
exit 1
