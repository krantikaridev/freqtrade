"""Replay last-90d backtest trades through the decision gate (#580).

Reads freqtrade `--export trades` zips + feather candles in repo.
Entry-time indicators only (no lookahead). One receipt row per decision.

Usage: python3 scripts/replay_gate.py --window-days 90 --out receipts/replay
"""
import argparse
import glob
import json
import os
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from decision_gate.gate import ConfidenceGate, Signal
from decision_gate.limits import LimitsConfig, RiskEnforcer
from decision_gate.receipts import ReceiptWriter
from scripts.gate_indicators import load_candles


def load_trades(zip_path: str):
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist()
                 if n.endswith(".json") and "config" not in n and "meta" not in n]
        data = json.loads(zf.read(names[0]))
    return next(iter(data["strategy"].values()))


def stats(trades: list, seed: float = 250.0):
    wins = [t for t in trades if t["pnl"] > 0]
    losses = [t for t in trades if t["pnl"] <= 0]
    gross_w = sum(t["pnl"] for t in wins)
    gross_l = -sum(t["pnl"] for t in losses)
    eq, peak, mdd = seed, seed, 0.0
    for t in trades:
        eq += t["pnl"]
        peak = max(peak, eq)
        if peak > 0:
            mdd = max(mdd, (peak - eq) / peak * 100)
    n = len(trades)
    if gross_l > 0:
        pf = round(gross_w / gross_l, 3)
    elif gross_w > 0:
        pf = float("inf")
    else:
        pf = 0.0
    tot = round(sum(t["pnl"] for t in trades), 2)
    return {"trades": n,
            "win_pct": round(100 * len(wins) / n, 1) if n else 0.0,
            "profit_abs": tot,
            "profit_pct": round(100 * tot / seed, 2),
            "max_dd_pct": round(mdd, 2), "profit_factor": pf}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window-days", type=int, default=90)
    ap.add_argument("--out", default="receipts/replay")
    ap.add_argument("--arm", default="TrendFollowingMaxDD_1h")
    args = ap.parse_args()
    strategy, tf = args.arm.rsplit("_", 1)
    zips = sorted(glob.glob("sweep/2026-10-06-stake250/%s.zip" % args.arm))
    if not zips:
        print("no export for %s" % args.arm, file=sys.stderr)
        sys.exit(1)
    m = load_trades(zips[0])
    all_trades = m["trades"]
    cutoff = max(t["close_timestamp"] for t in all_trades) - args.window_days * 86400 * 1000
    trades = [t for t in all_trades if t["open_timestamp"] >= cutoff]
    print("%s: %d/%d trades in last %dd" % (args.arm, len(trades), len(all_trades), args.window_days))
    candles = {}
    for pair in {t["pair"] for t in trades}:
        try:
            candles[pair] = load_candles(pair, tf)
        except FileNotFoundError as e:
            print("! no candles for %s: %s" % (pair, e), file=sys.stderr)
    os.makedirs(args.out, exist_ok=True)
    gate = ConfidenceGate()
    enf = RiskEnforcer(LimitsConfig(kill_switch_path=os.path.join(args.out, "KILL_SWITCH")))
    w = ReceiptWriter(os.path.join(args.out, "receipts-%s-%dd.csv" % (args.arm, args.window_days)))
    hist = defaultdict(list)
    gated, skipped = [], defaultdict(int)
    for t in sorted(trades, key=lambda x: x["open_timestamp"]):
        pair = t["pair"]
        side = "short" if t.get("is_short") else "long"
        df = candles.get(pair)
        if df is None:
            skipped["no_candles"] += 1
            continue
        entry = pd.Timestamp(t["open_timestamp"], unit="ms", tz="UTC")
        past = df[df["date"] < entry]
        if len(past) < 210:
            skipped["warmup"] += 1
            continue
        row = past.iloc[-1]
        hr_list = hist[(strategy, pair)][-20:]
        hr = sum(1 for x in hr_list if x > 0) / len(hr_list) if hr_list else -1.0
        spread = (row["ema_fast"] - row["ema_slow"]) / row["close"]
        if side == "short":
            spread = -spread
        sig = Signal(strategy, pair, side, t["open_timestamp"],
                     float(spread), float(row["adx"] or 0.0), float(hr))
        verdict = gate.judge(sig)
        route, limit_result, outcome, pnl = verdict.route, "", "n/a", 0.0
        stake = t.get("stake_amount", 0.0)
        if verdict.route == "trade":
            chk = enf.check(t["open_timestamp"], stake)
            if chk.allowed:
                enf.on_open()
                enf.on_close(t["close_timestamp"], t["profit_abs"])
                outcome, pnl = "taken", t["profit_abs"]
                limit_result = "allowed"
                gated.append({"pnl": pnl})
            elif chk.blocked_by == "max_position_pct":
                # all-in backtest stakes vs % cap: resize proportionally
                # instead of binary block, so the table compares the
                # confidence filter, not the sizing rule.
                frac = enf.equity * enf.config.max_position_pct / stake
                scaled = round(t["profit_abs"] * frac, 2)
                enf.on_open()
                enf.on_close(t["close_timestamp"], scaled)
                outcome, pnl = "taken(resized)", scaled
                limit_result = "resized:%.2f" % frac
                stake = round(enf.equity * enf.config.max_position_pct, 2)
                gated.append({"pnl": pnl})
            else:
                route = "blocked"
                limit_result = "blocked:" + chk.blocked_by
                skipped["limit:" + chk.blocked_by] += 1
        elif verdict.route == "wait":
            nxt = df[df["date"] >= entry]
            ok = len(nxt) >= 2 and (nxt.iloc[1]["date"] - entry).total_seconds() <= 7200
            if ok:
                chk = enf.check(t["open_timestamp"], stake)
                if chk.allowed:
                    enf.on_open()
                    enf.on_close(t["close_timestamp"], t["profit_abs"])
                    outcome, pnl = "taken(wait-confirmed)", t["profit_abs"]
                    limit_result = "allowed(wait-confirmed)"
                    gated.append({"pnl": pnl})
                elif chk.blocked_by == "max_position_pct":
                    frac = enf.equity * enf.config.max_position_pct / stake
                    scaled = round(t["profit_abs"] * frac, 2)
                    enf.on_open()
                    enf.on_close(t["close_timestamp"], scaled)
                    outcome, pnl = "taken(wait-confirmed,resized)", scaled
                    limit_result = "resized:%.2f" % frac
                    stake = round(enf.equity * enf.config.max_position_pct, 2)
                    gated.append({"pnl": pnl})
                else:
                    route = "blocked"
                    limit_result = "blocked:" + chk.blocked_by
                    skipped["limit:" + chk.blocked_by] += 1
            else:
                skipped["wait:no-confirmation"] += 1
        else:
            skipped["gate:skip"] += 1
        hist[(strategy, pair)].append(t["profit_abs"])
        w.write({"timestamp": datetime.fromtimestamp(t["open_timestamp"] / 1000, tz=timezone.utc).isoformat(),
                 "strategy": strategy, "pair": pair, "side": side,
                 "confidence": verdict.confidence, "votes": verdict.votes,
                 "route": route, "limits_checked": "kill,max_open,max_pos,daily_cap",
                 "limit_result": limit_result or verdict.reason,
                 "stake": round(stake, 2), "outcome": outcome, "pnl_abs": round(pnl, 2)})
    w.close()
    nogate = [{"pnl": t["profit_abs"]} for t in trades if t["pair"] in candles]
    s_off, s_on = stats(nogate), stats(gated)
    print("\n| mode | trades | win % | profit $ | profit % | max DD % | PF |")
    print("|---|---|---|---|---|---|---|")
    for label, s in (("no-gate", s_off), ("gate", s_on)):
        print("| %s | %d | %s | %s | %s | %s | %s |" % (
            label, s["trades"], s["win_pct"], s["profit_abs"],
            s["profit_pct"], s["max_dd_pct"], s["profit_factor"]))
    print("\nskipped:", dict(skipped))
    print("receipts:", w.path)


if __name__ == "__main__":
    main()

