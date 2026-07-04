"""
Base classes and interfaces for risk management.

Defines abstract interfaces that can be extended for specific risk implementations.
Provides foundation for position sizing, drawdown control, and dynamic allocation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading mode enumeration."""
    BACKTESTING = "backtesting"
    LIVE = "live"
    PAPER = "paper"


@dataclass
class PositionSizeParams:
    """Parameters for position sizing."""
    account_size: float
    risk_per_trade_pct: float
    volatility_adjustment: Optional[float] = None
    max_position_pct: Optional[float] = None


@dataclass
class DrawdownState:
    """Current drawdown state of the portfolio."""
    current_drawdown_pct: float
    peak_equity: float
    current_equity: float
    is_in_recovery: bool


class RiskManager(ABC):
    """
    Abstract base class for risk management.
    
    Defines the interface for overall risk control across the system.
    Should be extended with specific implementations for Hybrid Sleeve logic.
    """
    
    def __init__(self, mode, config: dict):
        """
        Initialize risk manager.
        
        Args:
            mode: Trading mode (backtesting, live, paper)
            config: Risk configuration dictionary
        """
        self.mode = mode
        self.config = config
        self.enabled = True
        logger.info(f"RiskManager initialized in {mode.value} mode")
    
    @abstractmethod
    def check_position_allowed(self, symbol: str, size: float) -> bool:
        """
        Check if a new position is allowed based on risk constraints.
        
        Args:
            symbol: Trading pair symbol
            size: Requested position size
            
        Returns:
            True if position is allowed, False otherwise
        """
        pass
    
    @abstractmethod
    def get_max_risk_amount(self) -> float:
        """
        Get maximum allowable risk amount for current portfolio state.
        
        Returns:
            Maximum risk amount in base currency
        """
        pass
    
    def update_state(self, current_equity: float, peak_equity: float) -> None:
        """
        Update risk manager with current portfolio state.
        Called periodically or after significant events.
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity since start/last reset
        """
        pass


class PositionSizer(ABC):
    """
    Abstract base class for position sizing logic.
    
    Handles calculation of position sizes based on risk parameters,
    account size, and current market conditions.
    """
    
    def __init__(self, config: dict):
        """
        Initialize position sizer.
        
        Args:
            config: Position sizing configuration
        """
        self.config = config
        self.risk_per_trade_pct = config.get("risk_per_trade_pct", 0.01)
        logger.info(f"PositionSizer initialized with {self.risk_per_trade_pct*100}% risk per trade")
    
    @abstractmethod
    def calculate_size(self, params: PositionSizeParams) -> float:
        """
        Calculate position size based on parameters.
        
        Args:
            params: Position sizing parameters
            
        Returns:
            Calculated position size
        """
        pass
    
    @abstractmethod
    def adjust_for_volatility(self, base_size: float, volatility: float) -> float:
        """
        Adjust position size based on market volatility.
        Higher volatility typically results in smaller sizes.
        
        Args:
            base_size: Base position size
            volatility: Current market volatility measure
            
        Returns:
            Adjusted position size
        """
        pass


class DrawdownManager(ABC):
    """
    Abstract base class for drawdown control.
    
    Monitors portfolio drawdown and triggers protective actions:
    - Reduced position sizes during drawdown
    - Emergency exit rules
    - Dynamic allocation reduction
    """
    
    def __init__(self, config: dict):
        """
        Initialize drawdown manager.
        
        Args:
            config: Drawdown control configuration
        """
        self.config = config
        self.max_drawdown_pct = config.get("max_portfolio_drawdown", 0.20)
        self.warning_threshold = config.get("drawdown_warning_threshold", 0.10)
        self.emergency_threshold = config.get("drawdown_emergency_threshold", 0.25)
        logger.info(
            f"DrawdownManager initialized: max={self.max_drawdown_pct*100}%, "
            f"warning={self.warning_threshold*100}%, emergency={self.emergency_threshold*100}%"
        )
    
    @abstractmethod
    def get_drawdown_state(self, current_equity: float, peak_equity: float) -> DrawdownState:
        """
        Calculate and return current drawdown state.
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity
            
        Returns:
            DrawdownState object with current status
        """
        pass
    
    @abstractmethod
    def get_risk_reduction_factor(self, drawdown_pct: float) -> float:
        """
        Calculate risk reduction factor based on drawdown level.
        
        Returns value between 0 and 1:
        - 1.0 = full risk (no drawdown)
        - 0.5 = 50% risk reduction
        - 0.0 = no trading (emergency)
        
        Args:
            drawdown_pct: Current drawdown percentage (0-1)
            
        Returns:
            Risk reduction factor (0-1)
        """
        pass
    
    @abstractmethod
    def is_emergency_exit_triggered(self, drawdown_pct: float) -> bool:
        """
        Check if emergency exit should be triggered.
        
        Args:
            drawdown_pct: Current drawdown percentage (0-1)
            
        Returns:
            True if emergency exit should trigger
        """
        pass
