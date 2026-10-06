"""Hard risk limits, enforced outside the strategy (paper-first, #580).

Limits (all on closed-trade equity, $250 seed):
  - max position % of equity (per-trade stake cap)
  - hard stop per trade (fraction of entry)
  - daily loss cap (halt new entries for the day)
  - max open trades
  - kill switch file (presence blocks all entries)

Unit tests cover each limit.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class LimitsConfig:
    seed: float = 250.0
    max_position_pct: float = 1.0  # fraction of equity per trade
    hard_stop_pct: float = 0.06  # exit if trade falls past -6%
    daily_loss_cap_pct: float = 0.05  # halt entries after -5% day
    max_open_trades: int = 1
    kill_switch_path: str = "KILL_SWITCH"


@dataclass
class LimitCheck:
    allowed: bool
    blocked_by: str = ""  # empty when allowed
    equity: float = 0.0


@dataclass
class RiskEnforcer:
    config: LimitsConfig = field(default_factory=LimitsConfig)
    open_trades: int = 0
    # day_key (YYYY-MM-DD UTC) -> realized pnl that day
    daily_pnl: dict = field(default_factory=dict)
    equity: float = 250.0

    def _today_key(self, ts_ms: int) -> str:
        return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")

    def kill_switch_active(self) -> bool:
        return Path(self.config.kill_switch_path).exists()

    def check(self, ts_ms: int, proposed_stake: float) -> LimitCheck:
        """Entry gate: kill switch, max open, position %, daily loss cap."""
        if self.kill_switch_active():
            return LimitCheck(False, "kill_switch", self.equity)
        if self.open_trades >= self.config.max_open_trades:
            return LimitCheck(False, "max_open_trades", self.equity)
        max_stake = self.equity * self.config.max_position_pct
        if proposed_stake > max_stake:
            return LimitCheck(False, "max_position_pct", self.equity)
        day = self._today_key(ts_ms)
        day_loss_cap = -self.equity * self.config.daily_loss_cap_pct
        if self.daily_pnl.get(day, 0.0) <= day_loss_cap:
            return LimitCheck(False, "daily_loss_cap", self.equity)
        return LimitCheck(True, "", self.equity)

    def stake_for(self, proposed: float) -> float:
        """Cap a proposed stake at max_position_pct of equity."""
        return min(proposed, self.equity * self.config.max_position_pct)

    def on_open(self) -> None:
        self.open_trades += 1

    def on_close(self, ts_ms: int, pnl_abs: float) -> None:
        self.open_trades = max(0, self.open_trades - 1)
        day = self._today_key(ts_ms)
        self.daily_pnl[day] = self.daily_pnl.get(day, 0.0) + pnl_abs
        self.equity += pnl_abs

    def hard_stop_hit(self, profit_ratio: float) -> bool:
        return profit_ratio <= -self.config.hard_stop_pct
