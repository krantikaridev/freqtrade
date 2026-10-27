#!/usr/bin/env bash
# tests/test_paper_pair_check.sh — hermetic coverage of scripts/paper_pair_check.sh
# verdicts: PASS(0), FAIL(1) for stopped / live-key / stale-heartbeat, BLOCKED(2).
# Runs entirely in a temp dir with a fake docker shim; never touches the real daemon.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHECK="$REPO/scripts/paper_pair_check.sh"
[ -f "$CHECK" ] || { echo "BLOCKED: check script missing at $CHECK"; exit 2; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
pass=0; failed=0

make_root() { # $1 = heartbeat age in minutes, $2 = dry_run true|false, $3 = key ""|"livekey"
  local root="$1" age_min="$2" dry="$3" key="$4" hb
  mkdir -p "$root/config" "$root/logs"
  python3 - "$root" "$dry" "$key" <<'PY'
import json, sqlite3, sys
root, dry, key = sys.argv[1], sys.argv[2] == "true", sys.argv[3]
for name, bot in (("config.dryrun.micro.nosol", "freqtrade-maxdd"),
                  ("config.dryrun.sweepema.nosol", "freqtrade-sweep-ema")):
    json.dump({"dry_run": dry, "dry_run_wallet": 250, "bot_name": bot,
               "exchange": {"name": "binance", "key": key, "secret": "",
                            "pair_whitelist": ["BTC/USDT:USDT"]}},
              open(f"{root}/config/{name}.json", "w"))
for db in ("tradesv3.dryrun.maxdd.sqlite", "tradesv3.dryrun.sweepema.sqlite"):
    con = sqlite3.connect(f"{root}/{db}")
    con.execute("create table trades (is_open int)")
    con.execute("insert into trades values (1)")
    con.commit(); con.close()
PY
  hb="$(python3 -c "
import datetime, sys
t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=int(sys.argv[1]))
print(t.strftime('%Y-%m-%d %H:%M:%S,000'))" "$age_min")"
  for f in freqtrade-maxdd freqtrade-sweepema; do
    printf "%s - freqtrade.worker - INFO - Bot heartbeat. PID=1, version='2026.9', state='RUNNING'\n" \
      "$hb" > "$root/logs/$f.log"
  done
  echo "$root"
}

fake() { # $1 = status the shim reports
  cat > "$TMP/docker-$2" <<EOF
#!/usr/bin/env bash
case "\$1" in
  info) exit 0 ;;
  inspect) echo "$1" ;;
  *) exit 0 ;;
esac
EOF
  chmod +x "$TMP/docker-$2"
}

expect() { # $1 label, $2 expected exit, then env for the run
  local label="$1" want="$2" got=""
  ( PAPER_ROOT="$PAPER_ROOT" DOCKER="$DOCKER" STALE_MIN="${STALE_MIN:-10}" bash "$CHECK" >"$TMP/out" 2>&1 )
  got=$?
  if [ "$got" = "$want" ]; then
    echo "ok   $label (exit $got)"; pass=$((pass + 1))
  else
    echo "NOT OK $label: want exit $want, got $got"; sed 's/^/       /' "$TMP/out" | head -6; failed=$((failed + 1))
  fi
}

fake running run
fake exited stop

# PASS: running, dry_run true, empty keys, fresh heartbeat
R="$(make_root "$TMP/pass" 0 true "")"; PAPER_ROOT="$R" DOCKER="$TMP/docker-run"; expect "PASS when both arms healthy" 0
# FAIL: containers not running
PAPER_ROOT="$R" DOCKER="$TMP/docker-stop"; expect "FAIL when a container is exited" 1
# FAIL: live key present
R2="$(make_root "$TMP/livekey" 0 true "ABC123key")"; PAPER_ROOT="$R2" DOCKER="$TMP/docker-run"; expect "FAIL when an exchange key is set" 1
# FAIL: dry_run disabled
R3="$(make_root "$TMP/nodry" 0 false "")"; PAPER_ROOT="$R3" DOCKER="$TMP/docker-run"; expect "FAIL when dry_run is false" 1
# FAIL: heartbeat older than STALE_MIN
R4="$(make_root "$TMP/stale" 90 true "")"; PAPER_ROOT="$R4" DOCKER="$TMP/docker-run"; expect "FAIL when heartbeat is stale" 1
# BLOCKED: no docker binary
PAPER_ROOT="$R" DOCKER="$TMP/no-such-docker"; expect "BLOCKED when docker is missing" 2
# BLOCKED: no heartbeat log at all
R5="$(make_root "$TMP/nologs" 0 true "")"; rm -rf "$R5/logs"; PAPER_ROOT="$R5" DOCKER="$TMP/docker-run"; expect "FAIL when heartbeat log absent" 1

echo "test_paper_pair_check: $pass passed, $failed failed"
[ "$failed" -eq 0 ] || exit 1
exit 0
