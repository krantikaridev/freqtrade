"""
Main entry point for Hybrid Sleeve trading system.

Demonstrates system initialization and basic setup.
"""

import asyncio
import logging
from pathlib import Path

from src.system.manager import SystemManager
from src.risk.base import TradingMode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    
    logger.info("=" * 80)
    logger.info("Hybrid Sleeve Trading System - Initialization Demo")
    logger.info("=" * 80)
    
    # Initialize system manager
    config_path = Path("config/system_config.json")
    manager = SystemManager(
        mode=TradingMode.BACKTESTING,
        config_path=config_path
    )
    
    # Initialize the system
    logger.info("\n--- System Initialization Phase ---")
    success = await manager.initialize()
    
    if not success:
        logger.error("System initialization failed!")
        return False
    
    # Print system status
    logger.info("\n--- System Status ---")
    status = manager.get_status()
    for key, value in status.items():
        logger.info(f"  {key}: {value}")
    
    # Print configuration
    logger.info("\n--- Configuration Loaded ---")
    logger.info(f"  Mode: {manager._config.get('mode')}")
    logger.info(f"  Risk Config: {manager._config.get('risk')}")
    logger.info(f"  Sleeves: {manager._config.get('sleeves')}")
    
    # Print sleeve allocations
    logger.info("\n--- Sleeve Allocations ---")
    allocations = manager.get_sleeve_allocation()
    for sleeve, pct in allocations.items():
        logger.info(f"  {sleeve}: {pct*100:.1f}%")
    
    # Test risk manager
    logger.info("\n--- Risk Manager Test ---")
    risk_mgr = manager.get_risk_manager()
    if risk_mgr:
        logger.info(f"  Type: {type(risk_mgr).__name__}")
        logger.info(f"  Position allowed (1st): {risk_mgr.check_position_allowed('BTC/USDT', 0.1)}")
        logger.info(f"  Max risk amount: {risk_mgr.get_max_risk_amount():.4f}")
        
        # Simulate some positions
        logger.info("  Opening 3 positions...")
        for i in range(3):
            allowed = risk_mgr.check_position_allowed(f'ASSET{i}/USDT', 0.1)
            logger.info(f"    Position {i+1}: {'ALLOWED' if allowed else 'DENIED'}")
            if allowed:
                risk_mgr.current_positions += 1
    
    # Test system start
    logger.info("\n--- System Start ---")
    if manager.start():
        logger.info("System started successfully!")
        logger.info(f"Running: {manager._running}")
        
        # Simulate equity update
        manager.update_equity(current_equity=100000, peak_equity=100000)
        logger.info(f"Equity updated: {manager._current_equity}")
        
        manager.stop()
        logger.info("System stopped")
    else:
        logger.error("Failed to start system")
    
    logger.info("\n" + "=" * 80)
    logger.info("Initialization Complete - System Ready for Trading")
    logger.info("=" * 80)
    
    return True


if __name__ == "__main__":
    asyncio.run(main())
