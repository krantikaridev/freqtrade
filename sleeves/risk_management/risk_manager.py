"""
Risk Management Module - Foundation for Hybrid Sleeve System

This module provides the core interfaces and base classes for managing risk
across multiple trading sleeves. It supports:
- Per-sleeve risk limits
- Portfolio-level drawdown control
- Dynamic risk allocation
- Position sizing based on volatility
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SleeveType(Enum):
    """Sleeve identifiers aligned with design doc."""
    X_SIGNAL_MOMENTUM = "x_signal_momentum"  # Sleeve 1
    TREND_FOLLOWING = "trend_following"  # Sleeve 2
    TACTICAL_MEAN_REVERSION = "tactical_mean_reversion"  # Sleeve 3


@dataclass
class RiskConfig:
    """Configuration for risk limits on a per-sleeve basis."""
    
    sleeve_id: str
    min_allocation: float  # Minimum % of portfolio risk budget
    max_allocation: float  # Maximum % of portfolio risk budget
    max_position_size: float  # Max size per position (in % of account)
    max_open_positions: int  # Max concurrent open positions
    stop_loss_pct: float  # Default stop loss percentage
    risk_per_trade: float  # Risk per single trade (% of portfolio)


@dataclass
class PortfolioRiskState:
    """Current state of portfolio risk metrics."""
    
    total_balance: float
    current_drawdown: float  # Current drawdown in %
    max_drawdown: float  # Max allowed drawdown in %
    allocated_risk_pct: float  # Total risk allocated as % of balance
    open_positions_count: int
    active_sleeves: int


class RiskManager:
    """
    Base class for managing risk across the hybrid sleeve system.
    
    This is a foundation interface. Implementations should:
    - Monitor drawdown levels
    - Enforce position size limits
    - Dynamically adjust allocations
    - Trigger risk reduction when thresholds are breached
    """
    
    def __init__(self, portfolio_max_drawdown: float = 0.20):
        """
        Initialize the Risk Manager.
        
        Args:
            portfolio_max_drawdown: Maximum allowed portfolio drawdown (default 20%)
        """
        self.portfolio_max_drawdown = portfolio_max_drawdown
        self.sleeve_configs: Dict[str, RiskConfig] = {}
        self.portfolio_state: Optional[PortfolioRiskState] = None
        logger.info(f"Risk Manager initialized with max drawdown: {portfolio_max_drawdown*100}%")
    
    def register_sleeve(self, config: RiskConfig) -> None:
        """
        Register a sleeve with its risk configuration.
        
        Args:
            config: RiskConfig for the sleeve
        """
        self.sleeve_configs[config.sleeve_id] = config
        logger.info(f"Registered sleeve: {config.sleeve_id}")
    
    def get_max_position_size(self, sleeve_id: str, account_balance: float) -> float:
        """
        Calculate maximum position size for a sleeve.
        
        Args:
            sleeve_id: Identifier of the sleeve
            account_balance: Current account balance
        
        Returns:
            Maximum position size in account currency
        """
        if sleeve_id not in self.sleeve_configs:
            logger.warning(f"Sleeve {sleeve_id} not registered")
            return 0.0
        
        config = self.sleeve_configs[sleeve_id]
        return account_balance * config.max_position_size
    
    def calculate_risk_per_trade(self, sleeve_id: str, account_balance: float) -> float:
        """
        Calculate risk allocation per trade for a sleeve.
        
        Args:
            sleeve_id: Identifier of the sleeve
            account_balance: Current account balance
        
        Returns:
            Risk amount in account currency
        """
        if sleeve_id not in self.sleeve_configs:
            logger.warning(f"Sleeve {sleeve_id} not registered")
            return 0.0
        
        config = self.sleeve_configs[sleeve_id]
        return account_balance * config.risk_per_trade
    
    def should_reduce_risk(self, current_drawdown: float) -> bool:
        """
        Determine if overall portfolio risk should be reduced.
        
        Args:
            current_drawdown: Current portfolio drawdown (0-1 scale)
        
        Returns:
            True if risk should be reduced
        """
        threshold = self.portfolio_max_drawdown * 0.75  # Reduce at 75% of max
        return current_drawdown > threshold
    
    def should_pause_trading(self, current_drawdown: float) -> bool:
        """
        Determine if all trading should be paused.
        
        Args:
            current_drawdown: Current portfolio drawdown (0-1 scale)
        
        Returns:
            True if trading should be paused
        """
        return current_drawdown >= self.portfolio_max_drawdown
    
    def validate_trade(self, sleeve_id: str, position_size: float, 
                      account_balance: float) -> bool:
        """
        Validate if a trade meets risk requirements.
        
        Args:
            sleeve_id: Identifier of the sleeve
            position_size: Proposed position size
            account_balance: Current account balance
        
        Returns:
            True if trade meets risk requirements
        """
        if sleeve_id not in self.sleeve_configs:
            logger.warning(f"Cannot validate: sleeve {sleeve_id} not registered")
            return False
        
        max_size = self.get_max_position_size(sleeve_id, account_balance)
        is_valid = position_size <= max_size
        
        if not is_valid:
            logger.warning(
                f"Trade rejected: position {position_size} exceeds max {max_size}"
            )
        
        return is_valid


class DynamicAllocationManager:
    """
    Base class for managing dynamic risk allocation across sleeves.
    
    This supports the design requirement of dynamic allocation based on:
    - Recent performance (7-14 days)
    - Market regime
    - Portfolio drawdown level
    
    Implementation to be refined with live performance data.
    """
    
    def __init__(self):
        self.sleeve_allocations: Dict[str, float] = {}
        logger.info("Dynamic Allocation Manager initialized")
    
    def set_allocation(self, sleeve_id: str, allocation_pct: float) -> None:
        """
        Set risk allocation for a sleeve.
        
        Args:
            sleeve_id: Identifier of the sleeve
            allocation_pct: Allocation as percentage (0-1 scale)
        """
        if not 0 <= allocation_pct <= 1:
            logger.error(f"Invalid allocation: {allocation_pct}. Must be 0-1.")
            return
        
        self.sleeve_allocations[sleeve_id] = allocation_pct
        logger.info(f"Set {sleeve_id} allocation to {allocation_pct*100}%")
    
    def get_allocation(self, sleeve_id: str) -> float:
        """
        Get current allocation for a sleeve.
        
        Args:
            sleeve_id: Identifier of the sleeve
        
        Returns:
            Allocation as percentage (0-1 scale)
        """
        return self.sleeve_allocations.get(sleeve_id, 0.0)
    
    def validate_allocations(self) -> bool:
        """
        Validate that allocations sum to 1.0 and follow design rules.
        
        Rules:
        - No single sleeve exceeds 60% (per design doc)
        - Allocations sum to ~1.0
        
        Returns:
            True if allocations are valid
        """
        max_single = 0.60
        total = sum(self.sleeve_allocations.values())
        
        if any(alloc > max_single for alloc in self.sleeve_allocations.values()):
            logger.error(f"Allocation exceeds {max_single*100}% limit")
            return False
        
        if not 0.95 <= total <= 1.05:  # Allow 5% tolerance
            logger.warning(f"Allocations sum to {total*100}%, expected ~100%")
            return False
        
        return True
