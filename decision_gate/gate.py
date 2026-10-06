"""Confidence gate: judge each strategy signal before any sizing.

Votes (each computed at signal time, no lookahead) are INDEPENDENT of
the strategy's own entry filter — otherwise the gate passes everything:
  1. fresh_trend - EMA spread just opened (young trend, not extended)
  2. momentum_ok - ADX strong but not exhausted (below exhaustion cap)
  3. regime_ok   - recent strategy+pair hit rate above floor (unknown passes)

Routes: high -> trade, medium -> wait (next candle), low -> skip.
"""
from dataclasses import dataclass


@dataclass
class Signal:
    strategy: str
    pair: str
    side: str  # "long" or "short"
    timestamp_ms: int
    ema_spread_pct: float  # signed: + means spread with-trend, - against
    adx: float
    hit_rate: float  # recent strategy+pair win rate 0..1, -1 if unknown


@dataclass
class Verdict:
    route: str  # trade | wait | skip
    confidence: str  # high | medium | low
    votes: int
    reason: str


class ConfidenceGate:
    def __init__(self, spread_min_pct: float = 0.001,
                 spread_max_pct: float = 0.03,
                 adx_min: float = 20.0, adx_max: float = 55.0,
                 hit_rate_min: float = 0.4):
        self.spread_min_pct = spread_min_pct
        self.spread_max_pct = spread_max_pct
        self.adx_min = adx_min
        self.adx_max = adx_max
        self.hit_rate_min = hit_rate_min

    def judge(self, sig: Signal) -> Verdict:
        votes = 0
        parts = []
        # vote 1: fresh trend — spread open but not extended (skip late entries)
        if self.spread_min_pct <= sig.ema_spread_pct <= self.spread_max_pct:
            votes += 1
            parts.append("fresh-trend")
        # vote 2: momentum alive — ADX confirms but not exhausted
        if self.adx_min <= sig.adx <= self.adx_max:
            votes += 1
            parts.append("momentum")
        # vote 3: regime — recent hit rate ok, or unknown (early trades pass)
        if sig.hit_rate < 0 or sig.hit_rate >= self.hit_rate_min:
            votes += 1
            parts.append("regime")

        if votes >= 3:
            return Verdict("trade", "high", votes, "3/3: " + "+".join(parts))
        if votes == 2:
            return Verdict("wait", "medium", votes,
                           "2/3 (%s): wait for next-candle confirmation" % "+".join(parts))
        return Verdict("skip", "low", votes,
                       "%d/3 votes: skip and log" % votes)
