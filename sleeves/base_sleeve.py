"""
Base Sleeve Template

Provides the foundation interface for all trading sleeves.
Each sleeve implementation extends this class with its own logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SleeveSignal:
    """Represents a trading signal from a sleeve."""
    sleeve_id: str
    symbol: str
    signal_type: str  # 'buy', 'sell', 'hold'
    confidence: float  # 0-1 scale
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class SleevePerformance:
    """Tracks performance metrics for a sleeve."""
    sleeve_id: str
    trades_executed: int
    win_rate: float  # 0-1 scale
    profit_loss_pct: float
    sharpe_ratio: Optional[float] = None
    drawdown_pct: float = 0.0
    last_updated: Optional[datetime] = None


class BaseSleeve(ABC):
    """
    Abstract base class for all trading sleeves.
    
    Each sleeve should:
    1. Monitor its designated market/timeframe
    2. Generate buy/sell signals
    3. Report performance metrics
    4. Respect risk limits from the RiskManager
    5. Respond to allocation adjustments
    """
    
    def __init__(self, sleeve_id: str, config: Dict):
        """
        Initialize a sleeve.
        
        Args:
            sleeve_id: Unique identifier for this sleeve
            config: Configuration dictionary for the sleeve
        """
        self.sleeve_id = sleeve_id
        self.config = config
        self.enabled = True
        self.current_allocation = 0.0
        self.active_positions: List[Dict] = []
        self.performance = SleevePerformance(
            sleeve_id=sleeve_id,
            trades_executed=0,
            win_rate=0.0,
            profit_loss_pct=0.0
        )
        logger.info(f"Initialized sleeve: {sleeve_id}")
    
    @abstractmethod
    def analyze(self, market_data: Dict) -> Optional[SleeveSignal]:
        """
        Analyze market data and generate a trading signal.
        
        Args:
            market_data: Dictionary containing OHLCV data and indicators
        
        Returns:
            SleeveSignal if a signal is generated, None otherwise
        """
        pass
    
    @abstractmethod
    def on_trade_executed(self, trade_info: Dict) -> None:
        """
        Called when a trade from this sleeve is executed.
        
        Args:
            trade_info: Dictionary with trade details (symbol, entry, size, etc.)
        """
        pass
    
    @abstractmethod
    def on_trade_closed(self, trade_result: Dict) -> None:
        """
        Called when a trade from this sleeve is closed (profit/loss realized).
        
        Args:
            trade_result: Dictionary with result (symbol, P&L, duration, etc.)
        """
        pass
    
    def update_allocation(self, new_allocation: float) -> None:
        """
        Update the sleeve's current risk allocation.
        
        Called by DynamicAllocationManager to adjust allocations dynamically.
        
        Args:
            new_allocation: New allocation as percentage (0-1 scale)
        """
        if not 0 <= new_allocation <= 1:
            logger.warning(f"Invalid allocation: {new_allocation}")
            return
        
        old_allocation = self.current_allocation
        self.current_allocation = new_allocation
        logger.info(
            f"Sleeve {self.sleeve_id} allocation updated: {old_allocation*100}% -> {new_allocation*100}%"
        )
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the sleeve.
        
        Called by system manager during emergencies or maintenance.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f"Sleeve {self.sleeve_id} {status}")
    
    def get_performance(self) -> SleevePerformance:
        """
        Get current performance metrics.
        
        Returns:
            SleevePerformance object with current metrics
        """
        self.performance.last_updated = datetime.utcnow()
        return self.performance
    
    def get_active_positions_count(self) -> int:
        """
        Get number of currently active positions.
        
        Returns:
            Count of active positions
        """
        return len(self.active_positions)
