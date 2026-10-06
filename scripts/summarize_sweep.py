#!/usr/bin/env python3
"""Build the sweep table from freqtrade backtest exports (#580, 6 Oct).

Reads <dir>/<strategy>_<timeframe>.zip (freqtrade's `--export trades` archive),
prints a markdown table and writes <dir>/SWEEP.csv.
Marks a row OVERFIT-RISK when it has fewer than 30 trades.
"""
import csv
import json
import sys
import zipfile
from pathlib import Path

OVERFIT_BELOW_TRADES = 30
COLS = ["strategy", "timeframe", "trades", "win_pct", "profit_pct",
        "max_dd_pct", "profit_factor", "sharpe", "overfit_risk"]


def load(path: Path):
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist()
                 if n.endswith(".json") and "config" not in n and "meta" not in n]
        data = json.loads(zf.read(names[0]))
    m = next(iter(data["strategy"].values()))
    trades = int(m.get("total_trades") or 0)
    winrate = float(m.get("winrate") or 0.0)
    return {
        "strategy": m.get("strategy_name") or path.stem,
        "timeframe": m.get("timeframe"),
        "trades": trades,
        "win_pct": round(winrate * 100, 1),
        "profit_pct": round(float(m.get("profit_total") or 0.0) * 100, 2),
        "max_dd_pct": round(float(m.get("max_drawdown_account") or 0.0) * 100, 2),
        "profit_factor": round(float(m.get("profit_factor") or 0.0), 3),
        "sharpe": round(float(m.get("sharpe") or 0.0), 2),
        "overfit_risk": trades < OVERFIT_BELOW_TRADES,
        "final_balance": round(float(m.get("final_balance") or 0.0), 2),
        "window": f"{m.get('backtest_start')} -> {m.get('backtest_end')}",
    }


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "sweep/2026-10-06")
    rows = []
    for path in sorted(out_dir.glob("*.zip")):
        try:
            rows.append(load(path))
        except Exception as exc:
            print(f"! unreadable {path.name}: {exc}", file=sys.stderr)
    rows.sort(key=lambda r: (r["profit_pct"], r["profit_factor"]), reverse=True)

    with (out_dir / "SWEEP.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLS + ["final_balance", "window"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print("| " + " | ".join(COLS) + " |")
    print("|" + "|".join(["---"] * len(COLS)) + "|")
    for r in rows:
        cells = [r["strategy"], r["timeframe"], str(r["trades"]), f"{r['win_pct']}%",
                 f"{r['profit_pct']}%", f"{r['max_dd_pct']}%", f"{r['profit_factor']}",
                 str(r["sharpe"]), "OVERFIT-RISK (<30 trades)" if r["overfit_risk"] else "ok"]
        print("| " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
