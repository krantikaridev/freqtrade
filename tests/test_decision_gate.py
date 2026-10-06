"""Unit tests for the decision gate + hard limits (stdlib only, #580).

Run: python3 -m unittest discover -s tests -v
Each hard limit has its own test. No live trading, no network.
"""
import csv
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from decision_gate.gate import ConfidenceGate, Signal
from decision_gate.limits import LimitsConfig, RiskEnforcer
from decision_gate.receipts import ReceiptWriter, RECEIPT_COLS


def _sig(**kw):
    base = dict(strategy="T", pair="BTC/USDT:USDT", side="long",
                timestamp_ms=1775700000000, ema_spread_pct=0.005,
                adx=30.0, hit_rate=0.6)
    base.update(kw)
    return Signal(**base)


class TestGate(unittest.TestCase):
    def test_high_trades_on_three_votes(self):
        v = ConfidenceGate().judge(_sig())
        self.assertEqual(v.route, "trade")
        self.assertEqual(v.confidence, "high")

    def test_medium_waits_on_two_votes(self):
        v = ConfidenceGate().judge(_sig(hit_rate=0.2))
        self.assertEqual(v.route, "wait")
        self.assertEqual(v.confidence, "medium")

    def test_low_skips_on_one_vote(self):
        v = ConfidenceGate().judge(_sig(hit_rate=0.2, adx=5.0))
        self.assertEqual(v.route, "skip")
        self.assertEqual(v.confidence, "low")

    def test_unknown_hit_rate_passes_regime(self):
        v = ConfidenceGate().judge(_sig(hit_rate=-1.0))
        self.assertEqual(v.route, "trade")

    def test_extended_spread_loses_fresh_trend_vote(self):
        v = ConfidenceGate().judge(_sig(ema_spread_pct=0.10))
        self.assertEqual(v.route, "wait")

    def test_exhausted_adx_loses_momentum_vote(self):
        v = ConfidenceGate().judge(_sig(adx=80.0))
        self.assertEqual(v.route, "wait")


class TestLimits(unittest.TestCase):
    def _enf(self, **kw):
        cfg = LimitsConfig(**kw)
        return RiskEnforcer(config=cfg)

    def test_max_position_pct_blocks_oversize(self):
        e = self._enf(seed=250.0, max_position_pct=0.5)
        e.equity = 250.0
        c = e.check(1775700000000, proposed_stake=200.0)
        self.assertFalse(c.allowed)
        self.assertEqual(c.blocked_by, "max_position_pct")

    def test_hard_stop_flags_past_threshold(self):
        e = self._enf(hard_stop_pct=0.06)
        self.assertTrue(e.hard_stop_hit(-0.07))
        self.assertFalse(e.hard_stop_hit(-0.05))

    def test_daily_loss_cap_halts_entries(self):
        e = self._enf(daily_loss_cap_pct=0.05)
        e.equity = 250.0
        ts = 1775700000000  # one UTC day
        e.on_close(ts, -13.0)  # worse than -5% of 250 = -12.5
        c = e.check(ts + 3600_000, proposed_stake=50.0)
        self.assertFalse(c.allowed)
        self.assertEqual(c.blocked_by, "daily_loss_cap")

    def test_max_open_trades_blocks_second(self):
        e = self._enf(max_open_trades=1)
        e.on_open()
        c = e.check(1775700000000, proposed_stake=50.0)
        self.assertFalse(c.allowed)
        self.assertEqual(c.blocked_by, "max_open_trades")

    def test_kill_switch_file_blocks_all(self):
        with tempfile.TemporaryDirectory() as d:
            ks = os.path.join(d, "KILL_SWITCH")
            e = self._enf(kill_switch_path=ks)
            self.assertTrue(e.check(1775700000000, 10.0).allowed)
            open(ks, "w").write("halt\n")
            c = e.check(1775700000000, 10.0)
            self.assertFalse(c.allowed)
            self.assertEqual(c.blocked_by, "kill_switch")

    def test_stake_capped_at_position_pct(self):
        e = self._enf(max_position_pct=0.5)
        e.equity = 250.0
        self.assertEqual(e.stake_for(200.0), 125.0)


class TestReceipts(unittest.TestCase):
    def test_receipt_csv_has_all_columns(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.csv")
            w = ReceiptWriter(p)
            w.write({"timestamp": "x", "strategy": "T", "route": "trade"})
            w.close()
            with open(p) as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["route"], "trade")
            for c in RECEIPT_COLS:
                self.assertIn(c, rows[0])


if __name__ == "__main__":
    unittest.main()
