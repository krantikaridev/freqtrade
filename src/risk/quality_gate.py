"""
Trade Quality Gate and Play Budget Management.

Implements quality filtering and trade budget tracking to prevent over-trading.
Key lesson from Nanoclaw: high rotation + low-quality trades + small capital = death spiral.

This module provides:
1. TradeQualityGate: Filters trades based on minimum quality thresholds
2. PlayBudget: Tracks and limits number of trades per period
3. QualityCheckpoint: Aggregates quality decisions with system state
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class QualityRejectionReason(Enum):
    """Enum for why a trade was rejected by quality gate."""
    ACCEPTED = "accepted"
    LOW_SIGNAL_STRENGTH = "low_signal_strength"
    INSUFFICIENT_EDGE = "insufficient_edge"
    BUDGET_EXHAUSTED = "budget_exhausted"
    DRAWDOWN_TOO_HIGH = "drawdown_too_high"
    SYSTEM_DISABLED = "system_disabled"


@dataclass
class QualityCheckResult:
    """Result of quality gate check on a trade."""
    allowed: bool
    reason: QualityRejectionReason
    signal_strength: float = 0.0
    edge_estimate: float = 0.0
    budget_remaining: int = 0
    drawdown_factor: float = 1.0
    
    def __str__(self) -> str:
        """Readable summary of quality check."""
        if self.allowed:
            return f"✓ ALLOWED (signal={self.signal_strength:.2f}, edge={self.edge_estimate:.3f})"
        else:
            return f"✗ REJECTED ({self.reason.value})"


@dataclass
class PlayBudgetConfig:
    """Configuration for play budget tracking."""
    max_trades_per_day: int = 10
    max_trades_per_session: Optional[int] = None
    reset_mode: str = "daily"  # "daily", "session", or "manual"
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_trades_per_day <= 0:
            raise ValueError("max_trades_per_day must be positive")
        if self.max_trades_per_session is not None and self.max_trades_per_session <= 0:
            raise ValueError("max_trades_per_session must be positive")


class PlayBudget:
    """
    Tracks and limits the number of trades allowed per period.
    
    Prevents the "high rotation trap": too many mediocre trades drain capital
    and add commission slippage costs.
    
    Usage:
        budget = PlayBudget(config)
        if budget.can_trade():
            # Execute trade
            budget.record_trade()
    """
    
    def __init__(self, config: PlayBudgetConfig):
        """
        Initialize play budget.
        
        Args:
            config: PlayBudgetConfig with budget limits
        """
        self.config = config
        self.trades_today = 0
        self.trades_in_session = 0
        self.session_start = datetime.utcnow()
        self.last_reset = datetime.utcnow()
        logger.info(
            f"PlayBudget initialized: {config.max_trades_per_day}/day"
            + (f", {config.max_trades_per_session}/session" if config.max_trades_per_session else "")
        )
    
    def can_trade(self) -> bool:
        """
        Check if we have budget remaining for a new trade.
        
        Returns:
            True if trade is allowed, False if budget exhausted
        """
        self._check_and_reset_if_needed()
        
        # Check daily limit
        if self.trades_today >= self.config.max_trades_per_day:
            logger.debug(f"Daily play budget exhausted: {self.trades_today}/{self.config.max_trades_per_day}")
            return False
        
        # Check session limit (if configured)
        if self.config.max_trades_per_session:
            if self.trades_in_session >= self.config.max_trades_per_session:
                logger.debug(
                    f"Session play budget exhausted: {self.trades_in_session}/{self.config.max_trades_per_session}"
                )
                return False
        
        return True
    
    def record_trade(self, symbol: str = "") -> None:
        """
        Record that a trade was executed.
        
        Args:
            symbol: Trading pair symbol (for logging)
        """
        self._check_and_reset_if_needed()
        
        self.trades_today += 1
        self.trades_in_session += 1
        
        logger.info(
            f"Trade recorded for {symbol}: {self.trades_today}/{self.config.max_trades_per_day} daily, "
            f"{self.trades_in_session}{'/' + str(self.config.max_trades_per_session) if self.config.max_trades_per_session else ''} session"
        )
    
    def get_trades_remaining(self) -> int:
        """Get number of trades remaining in budget."""
        self._check_and_reset_if_needed()
        return self.config.max_trades_per_day - self.trades_today
    
    def reset(self, reason: str = "manual") -> None:
        """
        Manually reset budget counters.
        
        Args:
            reason: Reason for reset (for logging)
        """
        logger.info(
            f"PlayBudget reset (reason: {reason}). "
            f"Previous: {self.trades_today} trades today, {self.trades_in_session} in session"
        )
        self.trades_today = 0
        self.trades_in_session = 0
        self.session_start = datetime.utcnow()
        self.last_reset = datetime.utcnow()
    
    def _check_and_reset_if_needed(self) -> None:
        """Check if daily reset is needed (based on config)."""
        if self.config.reset_mode == "daily":
            # Reset if a new day has started (simple check: midnight UTC)
            now = datetime.utcnow()
            if now.date() > self.last_reset.date():
                self.reset(reason="daily_reset")


class TradeQualityGate:
    """
    Gates trade execution based on quality thresholds.
    
    Prevents trading when:
    - Signal strength is too weak
    - Expected edge is negative or too small
    - System is in drawdown recovery (optional)
    - Budget is exhausted
    
    Key principle: **Quality over Quantity**
    Better to take fewer high-conviction trades than many mediocre ones.
    """
    
    def __init__(
        self,
        config: dict,
        play_budget: Optional[PlayBudget] = None
    ):
        """
        Initialize quality gate.
        
        Args:
            config: Configuration dictionary with keys:
                - min_signal_strength: Minimum signal strength (0-1)
                - min_edge_pct: Minimum expected edge percentage
                - drawdown_disable_trading: If True, disable trading during high drawdown
                - drawdown_threshold: Drawdown level to start filtering
            play_budget: PlayBudget instance (optional)
        """
        self.min_signal_strength = config.get("min_signal_strength", 0.60)
        self.min_edge_pct = config.get("min_edge_pct", 0.005)  # 0.5%
        self.drawdown_disable_trading = config.get("drawdown_disable_trading", True)
        self.drawdown_threshold = config.get("drawdown_threshold", 0.15)
        self.enabled = config.get("enabled", True)
        
        self.play_budget = play_budget
        
        logger.info(
            f"TradeQualityGate initialized: "
            f"signal≥{self.min_signal_strength:.2f}, "
            f"edge≥{self.min_edge_pct*100:.2f}%"
        )
    
    def check_trade_quality(
        self,
        symbol: str,
        signal_strength: float,
        edge_estimate: float,
        drawdown_pct: float = 0.0,
        system_enabled: bool = True
    ) -> QualityCheckResult:
        """
        Check if a trade meets quality gates.
        
        Args:
            symbol: Trading pair
            signal_strength: Signal strength (0-1 scale)
            edge_estimate: Expected edge as decimal (0.01 = 1%)
            drawdown_pct: Current portfolio drawdown (0-1 scale)
            system_enabled: Whether system is enabled for trading
            
        Returns:
            QualityCheckResult with decision and reasoning
        """
        
        # Check system enabled
        if not system_enabled:
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.SYSTEM_DISABLED,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0
            )
        
        # Check quality gate enabled
        if not self.enabled:
            logger.debug(f"Quality gate disabled, allowing trade {symbol}")
            result = QualityCheckResult(
                allowed=True,
                reason=QualityRejectionReason.ACCEPTED,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0
            )
            return result
        
        # Calculate drawdown factor (1.0 = no effect, 0.0 = block trading)
        drawdown_factor = self._get_drawdown_factor(drawdown_pct)
        
        # Check signal strength
        if signal_strength < self.min_signal_strength:
            logger.debug(
                f"Trade {symbol} rejected: signal strength {signal_strength:.2f} < {self.min_signal_strength:.2f}"
            )
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.LOW_SIGNAL_STRENGTH,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0,
                drawdown_factor=drawdown_factor
            )
        
        # Check edge
        if edge_estimate < self.min_edge_pct:
            logger.debug(
                f"Trade {symbol} rejected: edge {edge_estimate*100:.2f}% < {self.min_edge_pct*100:.2f}%"
            )
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.INSUFFICIENT_EDGE,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0,
                drawdown_factor=drawdown_factor
            )
        
        # Check drawdown threshold
        if drawdown_factor <= 0.0:
            logger.warning(
                f"Trade {symbol} rejected: drawdown {drawdown_pct*100:.1f}% too high "
                f"(threshold: {self.drawdown_threshold*100:.1f}%)"
            )
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.DRAWDOWN_TOO_HIGH,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0,
                drawdown_factor=drawdown_factor
            )
        
        # Check play budget
        if self.play_budget and not self.play_budget.can_trade():
            logger.warning(f"Trade {symbol} rejected: play budget exhausted")
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.BUDGET_EXHAUSTED,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate,
                budget_remaining=0,
                drawdown_factor=drawdown_factor
            )
        
        # All checks passed
        logger.info(
            f"Trade {symbol} ACCEPTED (signal={signal_strength:.2f}, edge={edge_estimate*100:.2f}%)"
        )
        return QualityCheckResult(
            allowed=True,
            reason=QualityRejectionReason.ACCEPTED,
            signal_strength=signal_strength,
            edge_estimate=edge_estimate,
            budget_remaining=self.play_budget.get_trades_remaining() if self.play_budget else 0,
            drawdown_factor=drawdown_factor
        )
    
    def _get_drawdown_factor(self, drawdown_pct: float) -> float:
        """
        Calculate drawdown factor (reduces trading aggressiveness in drawdown).
        
        If drawdown_disable_trading is False, returns 1.0 (no effect).
        Otherwise:
        - Below threshold: 1.0 (full trading)
        - At threshold: 0.5 (50% reduction)
        - Above threshold: 0.0 (no trading)
        
        Args:
            drawdown_pct: Current drawdown (0-1)
            
        Returns:
            Factor between 0 and 1
        """
        if not self.drawdown_disable_trading:
            return 1.0
        
        if drawdown_pct <= self.drawdown_threshold:
            return 1.0
        
        # Linear interpolation from threshold to complete disable at 2x threshold
        max_threshold = self.drawdown_threshold * 2.0
        if drawdown_pct >= max_threshold:
            return 0.0
        
        factor = 1.0 - (drawdown_pct - self.drawdown_threshold) / self.drawdown_threshold
        return max(0.0, min(1.0, factor))
