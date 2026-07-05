"""
System Manager - Central orchestration and initialization.

Handles system initialization, configuration loading, risk management setup,
and provides hooks for sleeve coordination. This is the main entry point
for the Hybrid Sleeve trading system.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from src.system.config import ConfigLoader
from src.risk.base import RiskManager, TradingMode
from src.risk.simple import SimpleRiskManager
from src.risk.quality_gate import TradeQualityGate, QualityCheckResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemManager:
    """
    Central manager for the Hybrid Sleeve trading system.
    
    Responsibilities:
    - System initialization and startup
    - Configuration loading and validation
    - Risk management setup (including quality gates)
    - Sleeve coordination (foundation for future)
    - System state monitoring
    - Trade quality checking
    
    Usage:
        manager = SystemManager(mode=TradingMode.BACKTESTING)
        await manager.initialize()
        # System is ready for trading
        
        # Check trade quality before execution
        quality_result = manager.check_trade_quality(
            symbol="BTC/USD",
            signal_strength=0.75,
            edge_estimate=0.02
        )
        if quality_result.allowed:
            # Execute trade
            pass
    """
    
    def __init__(
        self,
        mode: TradingMode = TradingMode.BACKTESTING,
        config_path: Optional[Path] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize System Manager.
        
        Args:
            mode: Trading mode (backtesting, live, paper)
            config_path: Path to configuration file
            config_overrides: Dictionary of config overrides for programmatic setup
        """
        self.mode = mode
        self.config_path = config_path
        self.config_overrides = config_overrides or {}
        
        # Components (initialized during setup)
        self._config: Optional[Dict[str, Any]] = None
        self._config_loader: Optional[ConfigLoader] = None
        self._risk_manager: Optional[RiskManager] = None
        self._quality_gate: Optional[TradeQualityGate] = None
        
        # State tracking
        self._initialized = False
        self._running = False
        self._peak_equity = 0.0
        self._current_equity = 0.0
        self._current_drawdown = 0.0
        
        logger.info(f"SystemManager created (mode={mode.value})")
    
    async def initialize(self) -> bool:
        """
        Initialize the system.
        
        Execution order:
        1. Load configuration
        2. Validate configuration
        3. Initialize risk management (including quality gate)
        4. Set system to ready state
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Starting system initialization...")
            
            # Step 1: Load configuration
            if not self._load_configuration():
                logger.error("Configuration loading failed")
                return False
            
            # Step 2: Initialize risk management
            if not self._initialize_risk_management():
                logger.error("Risk management initialization failed")
                return False
            
            # Step 3: Extract quality gate from risk manager
            if hasattr(self._risk_manager, 'quality_gate'):
                self._quality_gate = self._risk_manager.quality_gate
                logger.info("Quality gate attached from risk manager")
            
            # Step 4: System ready
            self._initialized = True
            logger.info("System initialization completed successfully")
            return True
        
        except Exception as e:
            logger.error(f"System initialization failed with exception: {e}", exc_info=True)
            return False
    
    def start(self) -> bool:
        """
        Start the trading system.
        
        Requires that initialize() has been called first.
        
        Returns:
            True if startup successful, False otherwise
        """
        if not self._initialized:
            logger.error("Cannot start: System not initialized. Call initialize() first.")
            return False
        
        try:
            logger.info(f"Starting trading system in {self.mode.value} mode...")
            self._running = True
            logger.info("Trading system started")
            return True
        except Exception as e:
            logger.error(f"Failed to start trading system: {e}", exc_info=True)
            return False
    
    def stop(self) -> None:
        """Stop the trading system."""
        if self._running:
            logger.info("Stopping trading system...")
            self._running = False
            logger.info("Trading system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current system status.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "initialized": self._initialized,
            "running": self._running,
            "mode": self.mode.value,
            "risk_manager": type(self._risk_manager).__name__ if self._risk_manager else None,
            "peak_equity": self._peak_equity,
            "current_equity": self._current_equity,
            "current_drawdown": self._current_drawdown,
        }
        
        # Add quality gate status
        if self._quality_gate:
            status["quality_gate_enabled"] = self._quality_gate.enabled
            status["quality_gate"] = {
                "min_signal_strength": self._quality_gate.min_signal_strength,
                "min_edge_pct": self._quality_gate.min_edge_pct,
            }
        
        # Add play budget status
        if self._risk_manager and hasattr(self._risk_manager, 'play_budget'):
            budget = self._risk_manager.play_budget
            status["play_budget"] = {
                "max_trades_per_day": budget.config.max_trades_per_day,
                "trades_today": budget.trades_today,
                "remaining_budget": budget.get_trades_remaining()
            }
        
        return status
    
    def get_risk_manager(self) -> Optional[RiskManager]:
        """
        Get the risk manager instance.
        
        Returns:
            RiskManager instance or None if not initialized
        """
        return self._risk_manager
    
    def check_trade_quality(
        self,
        symbol: str,
        signal_strength: float,
        edge_estimate: float,
        system_enabled: bool = True
    ) -> QualityCheckResult:
        """
        Check if a trade meets quality requirements.
        
        This is the main entry point for trade quality decisions.
        Should be called BEFORE attempting to open any position.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USD")
            signal_strength: Signal strength (0-1 scale)
            edge_estimate: Expected edge as decimal (0.01 = 1%)
            system_enabled: Whether system is enabled for trading
            
        Returns:
            QualityCheckResult with decision and reasons
            
        Example:
            result = manager.check_trade_quality("BTC/USD", 0.75, 0.02)
            if result.allowed:
                logger.info(f"Trade approved: {result}")
                # Execute trade and record it
                manager.record_trade_execution("BTC/USD")
            else:
                logger.debug(f"Trade rejected: {result}")
        """
        if not self._initialized:
            logger.error("Cannot check quality: System not initialized")
            from src.risk.quality_gate import QualityCheckResult, QualityRejectionReason
            return QualityCheckResult(
                allowed=False,
                reason=QualityRejectionReason.SYSTEM_DISABLED,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate
            )
        
        if not self._quality_gate:
            logger.warning("Quality gate not available, allowing trade")
            from src.risk.quality_gate import QualityCheckResult, QualityRejectionReason
            return QualityCheckResult(
                allowed=True,
                reason=QualityRejectionReason.ACCEPTED,
                signal_strength=signal_strength,
                edge_estimate=edge_estimate
            )
        
        return self._quality_gate.check_trade_quality(
            symbol=symbol,
            signal_strength=signal_strength,
            edge_estimate=edge_estimate,
            drawdown_pct=self._current_drawdown,
            system_enabled=system_enabled and self._running
        )
    
    def record_trade_execution(self, symbol: str) -> None:
        """
        Record that a trade was executed.
        Should be called after trade is successfully opened.
        
        Args:
            symbol: Trading pair symbol
        """
        if self._risk_manager and hasattr(self._risk_manager, 'play_budget'):
            self._risk_manager.play_budget.record_trade(symbol)
    
    def update_equity(self, current_equity: float, peak_equity: Optional[float] = None) -> None:
        """
        Update system with current equity information.
        
        Should be called periodically to keep risk management updated.
        
        Args:
            current_equity: Current account equity
            peak_equity: Peak equity (if None, uses previous peak)
        """
        self._current_equity = current_equity
        if peak_equity is not None:
            self._peak_equity = max(self._peak_equity, peak_equity)
        else:
            if self._peak_equity == 0:
                self._peak_equity = current_equity
        
        # Calculate current drawdown
        if self._peak_equity > 0:
            self._current_drawdown = (self._peak_equity - self._current_equity) / self._peak_equity
        
        if self._risk_manager:
            self._risk_manager.update_state(self._current_equity, self._peak_equity)
    
    # =========================================================================
    # Private Methods
    # =========================================================================
    
    def _load_configuration(self) -> bool:
        """
        Load and validate system configuration.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Loading configuration...")
            
            self._config_loader = ConfigLoader(self.config_path)
            self._config = self._config_loader.load()
            
            # Apply programmatic overrides
            if self.config_overrides:
                logger.info(f"Applying {len(self.config_overrides)} configuration overrides...")
                self._config.update(self.config_overrides)
            
            logger.info("Configuration loaded successfully")
            logger.debug(f"Config: {self._config}")
            return True
        
        except Exception as e:
            logger.error(f"Configuration loading failed: {e}", exc_info=True)
            return False
    
    def _initialize_risk_management(self) -> bool:
        """
        Initialize risk management components.
        
        Currently uses SimpleRiskManager with quality gate and play budget.
        Can be extended to use more sophisticated implementations.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing risk management...")
            
            risk_config = self._config.get("risk", {})
            
            # Use SimpleRiskManager (includes quality gate and play budget)
            self._risk_manager = SimpleRiskManager(self.mode, risk_config)
            
            logger.info(f"Risk manager initialized: {type(self._risk_manager).__name__}")
            return True
        
        except Exception as e:
            logger.error(f"Risk management initialization failed: {e}", exc_info=True)
            return False
    
    # =========================================================================
    # Placeholder Methods for Future Sleeve Coordination
    # =========================================================================
    
    def get_sleeve_allocation(self) -> Dict[str, float]:
        """
        Get current sleeve risk allocations.
        
        Returns:
            Dictionary mapping sleeve names to allocation percentages
        """
        # Placeholder for future sleeve coordination
        sleeves_config = self._config.get("sleeves", {})
        return sleeves_config.get("default_allocation", {})
    
    def update_sleeve_performance(self, sleeve_name: str, performance_data: Dict[str, Any]) -> None:
        """
        Update performance data for a sleeve.
        
        Will be used in future for dynamic allocation adjustments.
        
        Args:
            sleeve_name: Name of the sleeve
            performance_data: Performance metrics
        """
        # Placeholder for future dynamic allocation logic
        logger.debug(f"Sleeve {sleeve_name} performance update: {performance_data}")
    
    def get_dynamic_allocation(self) -> Dict[str, float]:
        """
        Get dynamic allocation adjustments based on sleeve performance.
        
        Currently returns default allocation. Will be enhanced with
        dynamic logic in future iterations.
        
        Returns:
            Dictionary mapping sleeve names to dynamic allocations
        """
        # Placeholder: Currently returns static allocation
        # Future: Will compute based on sleeve performance metrics
        return self.get_sleeve_allocation()
