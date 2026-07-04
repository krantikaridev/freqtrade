"""
Simple/default implementations of risk management interfaces.

Provides basic but functional implementations for position sizing,
drawdown management, and risk control. Can be extended for more sophisticated logic.
"""

import logging
from src.risk.base import (
    RiskManager, PositionSizer, DrawdownManager,
    PositionSizeParams, DrawdownState, TradingMode
)

logger = logging.getLogger(__name__)


class SimpleRiskManager(RiskManager):
    """
    Simple risk manager implementation.
    
    Provides basic position control based on fixed risk per trade
    and drawdown thresholds. Foundation for more complex logic.
    """
    
    def __init__(self, mode: TradingMode, config: dict):
        """
        Initialize simple risk manager.
        
        Args:
            mode: Trading mode
            config: Risk configuration
        """
        super().__init__(mode, config)
        self.max_positions = config.get("max_concurrent_positions", 5)
        self.max_risk_pct = config.get("max_risk_per_trade_pct", 0.01)
        self.current_positions = 0
        self._risk_budget = 1.0
    
    def check_position_allowed(self, symbol: str, size: float) -> bool:
        """
        Check if position is allowed.
        
        Constraints:
        - Not exceeding max concurrent positions
        - Not exceeding available risk budget
        """
        if self.current_positions >= self.max_positions:
            logger.warning(
                f"Cannot open position in {symbol}: "
                f"max positions ({self.max_positions}) reached"
            )
            return False
        
        if self._risk_budget <= 0:
            logger.warning(f"Cannot open position in {symbol}: risk budget exhausted")
            return False
        
        return True
    
    def get_max_risk_amount(self) -> float:
        """
        Get maximum allowable risk amount.
        
        Returns:
            Maximum risk in percentage (relative to account)
        """
        return self._risk_budget * self.max_risk_pct
    
    def update_state(self, current_equity: float, peak_equity: float) -> None:
        """
        Update risk state. Placeholder for future state tracking.
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity
        """
        # Will be enhanced with drawdown tracking and dynamic adjustment
        pass


class SimplePositionSizer(PositionSizer):
    """
    Simple position sizing based on fixed risk percentage.
    
    Calculates position size as: account_size * risk_per_trade_pct / stop_loss_pct
    Provides volatility adjustment to reduce size in high volatility.
    """
    
    def __init__(self, config: dict):
        """
        Initialize simple position sizer.
        
        Args:
            config: Position sizing configuration
        """
        super().__init__(config)
        self.volatility_scale = config.get("volatility_scale", 2.0)
    
    def calculate_size(self, params: PositionSizeParams) -> float:
        """
        Calculate position size using Kelly-like formula.
        
        Args:
            params: Position sizing parameters
            
        Returns:
            Calculated position size (in quote currency)
        """
        # Basic formula: risk_amount / stop_loss_pct
        risk_amount = params.account_size * params.risk_per_trade_pct
        
        # Add volatility adjustment if provided
        if params.volatility_adjustment:
            risk_amount /= params.volatility_adjustment
        
        # Apply max position constraint if provided
        if params.max_position_pct:
            max_position = params.account_size * params.max_position_pct
            size = min(risk_amount, max_position)
        else:
            size = risk_amount
        
        logger.debug(
            f"Calculated position size: {size:.4f} "
            f"(account={params.account_size}, risk_pct={params.risk_per_trade_pct*100}%)"
        )
        return size
    
    def adjust_for_volatility(self, base_size: float, volatility: float) -> float:
        """
        Adjust position size inversely with volatility.
        
        Higher volatility → smaller position
        Lower volatility → larger position (up to base size)
        
        Args:
            base_size: Base position size
            volatility: Volatility measure (typically 0-100 or similar range)
            
        Returns:
            Adjusted position size
        """
        # Simple linear scaling: divide by volatility
        # Assumes volatility is normalized (e.g., ATR relative to price)
        if volatility <= 0:
            return base_size
        
        adjusted_size = base_size / (1.0 + self.volatility_scale * (volatility - 1.0))
        adjusted_size = max(0, min(base_size, adjusted_size))  # Clamp between 0 and base_size
        
        logger.debug(f"Volatility adjustment: {base_size:.4f} → {adjusted_size:.4f} (vol={volatility})")
        return adjusted_size


class SimpleDrawdownManager(DrawdownManager):
    """
    Simple drawdown manager implementation.
    
    Monitors drawdown and reduces risk proportionally.
    Triggers emergency exit at max threshold.
    """
    
    def __init__(self, config: dict):
        """
        Initialize simple drawdown manager.
        
        Args:
            config: Drawdown configuration
        """
        super().__init__(config)
    
    def get_drawdown_state(self, current_equity: float, peak_equity: float) -> DrawdownState:
        """
        Calculate drawdown state.
        
        Args:
            current_equity: Current equity
            peak_equity: Peak equity
            
        Returns:
            DrawdownState with current values
        """
        if peak_equity <= 0:
            drawdown_pct = 0.0
        else:
            drawdown_pct = (peak_equity - current_equity) / peak_equity
        
        is_in_recovery = current_equity >= peak_equity * 0.95  # Within 5% of peak
        
        return DrawdownState(
            current_drawdown_pct=drawdown_pct,
            peak_equity=peak_equity,
            current_equity=current_equity,
            is_in_recovery=is_in_recovery
        )
    
    def get_risk_reduction_factor(self, drawdown_pct: float) -> float:
        """
        Calculate risk reduction factor.
        
        Linear interpolation from 1.0 (no drawdown) to 0.0 (emergency):
        - 0% drawdown: factor = 1.0
        - 10% drawdown: factor = 1.0
        - 20% drawdown (max): factor = 0.0
        
        Args:
            drawdown_pct: Drawdown percentage (0-1)
            
        Returns:
            Risk reduction factor (0-1)
        """
        if drawdown_pct <= self.warning_threshold:
            return 1.0
        elif drawdown_pct >= self.max_drawdown_pct:
            return 0.0
        else:
            # Linear interpolation
            range_pct = self.max_drawdown_pct - self.warning_threshold
            reduction = (drawdown_pct - self.warning_threshold) / range_pct
            return 1.0 - reduction
    
    def is_emergency_exit_triggered(self, drawdown_pct: float) -> bool:
        """
        Check if emergency exit should trigger.
        
        Args:
            drawdown_pct: Drawdown percentage (0-1)
            
        Returns:
            True if drawdown exceeds emergency threshold
        """
        return drawdown_pct >= self.emergency_threshold
