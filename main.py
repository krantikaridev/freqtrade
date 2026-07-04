#!/usr/bin/env python3
"""
Hybrid Sleeve Trading System - Entry Point

Initializes the system and provides a basic trading loop.
"""

import os
import sys
import logging
from typing import Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sleeves.system_manager import HybridSleeveSystem
from sleeves.implementations import (
    XSignalMomentumSleeve,
    TrendFollowingSleeve,
    TacticalMeanReversionSleeve
)
from sleeves.risk_management.risk_manager import RiskConfig
from sleeves.utils.monitoring import setup_logging
from sleeves.utils.config import load_environment_config, load_yaml_config, interpolate_env_vars

logger = logging.getLogger(__name__)


def load_system_config() -> Dict:
    """
    Load system configuration from environment and config files.
    
    Returns:
        Merged configuration dictionary
    """
    # Load environment config
    env_config = load_environment_config()
    
    # Load base YAML config
    base_config_path = 'config/config.base.yaml'
    if os.path.exists(base_config_path):
        base_yaml = load_yaml_config(base_config_path)
        base_yaml = interpolate_env_vars(base_yaml)
    else:
        base_yaml = {}
    
    # Load environment-specific config
    env = env_config.get('environment', 'dev')
    env_config_path = f'config/config.{env}.yaml'
    if os.path.exists(env_config_path):
        env_yaml = load_yaml_config(env_config_path)
        env_yaml = interpolate_env_vars(env_yaml)
    else:
        env_yaml = {}
    
    # Merge configs (env-specific overrides base)
    config = {**base_yaml, **env_yaml, **env_config}
    return config


def create_risk_configs() -> Dict[str, RiskConfig]:
    """
    Create risk configurations for each sleeve.
    
    Aligned with Hybrid Sleeve Design v1:
    - Sleeve 1 (X-Signal): 45-55% allocation, aggressive
    - Sleeve 2 (Trend): 25-35% allocation, stable
    - Sleeve 3 (Reversion): 15-25% allocation, tactical
    
    Returns:
        Dictionary mapping sleeve_id to RiskConfig
    """
    return {
        "x_signal_momentum": RiskConfig(
            sleeve_id="x_signal_momentum",
            min_allocation=0.45,
            max_allocation=0.55,
            max_position_size=0.10,  # 10% of account per position
            max_open_positions=5,
            stop_loss_pct=0.05,
            risk_per_trade=0.02  # 2% risk per trade
        ),
        "trend_following": RiskConfig(
            sleeve_id="trend_following",
            min_allocation=0.25,
            max_allocation=0.35,
            max_position_size=0.08,
            max_open_positions=4,
            stop_loss_pct=0.07,
            risk_per_trade=0.015  # 1.5% risk per trade
        ),
        "tactical_mean_reversion": RiskConfig(
            sleeve_id="tactical_mean_reversion",
            min_allocation=0.15,
            max_allocation=0.25,
            max_position_size=0.05,
            max_open_positions=3,
            stop_loss_pct=0.03,
            risk_per_trade=0.01  # 1% risk per trade
        )
    }


def initialize_system() -> HybridSleeveSystem:
    """
    Initialize the Hybrid Sleeve System.
    
    Returns:
        Initialized HybridSleeveSystem instance
    """
    # Load configuration
    config = load_system_config()
    logger.info(f"System configuration loaded (environment: {config.get('environment', 'dev')})")
    
    # Create system
    system = HybridSleeveSystem(config)
    
    # Create risk configs
    risk_configs = create_risk_configs()
    
    # Create and register sleeves
    sleeves = {
        "x_signal_momentum": XSignalMomentumSleeve(config),
        "trend_following": TrendFollowingSleeve(config),
        "tactical_mean_reversion": TacticalMeanReversionSleeve(config),
    }
    
    for sleeve_id, sleeve in sleeves.items():
        system.register_sleeve(sleeve, risk_configs[sleeve_id])
    
    logger.info(f"System initialized with {len(sleeves)} sleeves")
    return system


def main():
    """
    Main entry point for the trading system.
    """
    # Setup logging
    setup_logging(log_level='INFO')
    logger.info("Starting Hybrid Sleeve Trading System...")
    
    try:
        # Initialize system
        system = initialize_system()
        
        # Start system
        if not system.start():
            logger.error("Failed to start system")
            return 1
        
        # Print initial status
        system.print_status()
        
        logger.info("System ready. Press Ctrl+C to stop.")
        
        # Basic trading loop (placeholder)
        import time
        try:
            while system.is_running:
                # TODO: Implement actual trading loop
                # - Fetch market data
                # - Process signals from all sleeves
                # - Execute trades
                # - Update allocations
                # - Monitor health
                
                time.sleep(10)  # Sleep 10 seconds between cycles
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        
        finally:
            system.stop()
            logger.info("System stopped")
    
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
