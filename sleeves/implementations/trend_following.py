"""
Trend Following Sleeve (Sleeve 2)

Technical trend continuation strategy with narrative strength.
- Timeframe: 3-21 days
- Style: Trend following, stable returns
- Initial allocation: 25-35%
"""

from typing import Dict, Optional
import logging
from .base_sleeve import BaseSleeve, SleeveSignal

logger = logging.getLogger(__name__)


class TrendFollowingSleeve(BaseSleeve):
    """
    Trend Following Sleeve implementation.
    
    Focuses on identifying and riding strong trends with technical
    indicators and narrative confirmation.
    """
    
    def __init__(self, config: Dict):
        # Import here to avoid circular dependency
        from .base_sleeve import BaseSleeve as BS
        super().__init__("trend_following", config)
        self.trend_strength_threshold = config.get('trend_strength_threshold', 0.6)
        self.min_trend_bars = config.get('min_trend_bars', 5)
        logger.info(f"Trend Following Sleeve initialized")
    
    def analyze(self, market_data: Dict) -> Optional[SleeveSignal]:
        """
        Analyze market for trending opportunities.
        
        Placeholder: Will integrate with trend detection logic.
        
        Args:
            market_data: Market OHLCV data with indicators
        
        Returns:
            SleeveSignal if strong trend detected
        """
        # TODO: Implement trend detection
        # This should check for:
        # - Strong uptrend or downtrend
        # - Trend strength confirmation
        # - Narrative support
        # - Entry setup on pullback
        
        logger.debug(f"Analyzing trends for {self.sleeve_id}")
        return None
    
    def on_trade_executed(self, trade_info: Dict) -> None:
        """
        Handle execution of a trade from this sleeve.
        
        Args:
            trade_info: Trade details
        """
        symbol = trade_info.get('symbol')
        side = trade_info.get('side')
        amount = trade_info.get('amount')
        
        self.active_positions.append(trade_info)
        self.performance.trades_executed += 1
        
        logger.info(
            f"[{self.sleeve_id}] Trade executed: {side} {amount} {symbol}"
        )
    
    def on_trade_closed(self, trade_result: Dict) -> None:
        """
        Handle closure of a trade from this sleeve.
        
        Args:
            trade_result: Trade result with P&L
        """
        symbol = trade_result.get('symbol')
        pnl_pct = trade_result.get('pnl_pct', 0)
        
        # Update performance
        if pnl_pct > 0:
            wins = (self.performance.win_rate * self.performance.trades_executed) + 1
            self.performance.win_rate = wins / (self.performance.trades_executed + 1)
        
        self.performance.profit_loss_pct += pnl_pct
        
        logger.info(
            f"[{self.sleeve_id}] Trade closed: {symbol} P&L: {pnl_pct:.2f}%"
        )
        
        # Remove from active positions
        self.active_positions = [
            pos for pos in self.active_positions 
            if pos.get('symbol') != symbol
        ]
