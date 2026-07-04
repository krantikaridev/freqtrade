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
    - Risk management setup
    - Sleeve coordination (foundation for future)
    - System state monitoring
    
    Usage:
        manager = SystemManager(mode=TradingMode.BACKTESTING)
        await manager.initialize()
        # System is ready for trading
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
        
        # State tracking
        self._initialized = False
        self._running = False
        self._peak_equity = 0.0
        self._current_equity = 0.0
        
        logger.info(f"SystemManager created (mode={mode.value})")
    
    async def initialize(self) -> bool:
        """
        Initialize the system.
        
        Execution order:
        1. Load configuration
        2. Validate configuration
        3. Initialize risk management
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
            
            # Step 3: System ready
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
        return {
            "initialized": self._initialized,
            "running": self._running,
            "mode": self.mode.value,
            "risk_manager": type(self._risk_manager).__name__ if self._risk_manager else None,
            "peak_equity": self._peak_equity,
            "current_equity": self._current_equity,
        }
    
    def get_risk_manager(self) -> Optional[RiskManager]:
        """
        Get the risk manager instance.
        
        Returns:
            RiskManager instance or None if not initialized
        """
        return self._risk_manager
    
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
        
        Currently uses SimpleRiskManager. Can be extended to use
        more sophisticated implementations.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing risk management...")
            
            risk_config = self._config.get("risk", {})
            
            # For now, use SimpleRiskManager
            # In future, this could be factory-based or configurable
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
