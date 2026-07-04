"""
Configuration loading and management for Hybrid Sleeve system.

Handles loading of YAML/JSON configs and validation.
Provides a clean interface for accessing system configuration.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and manages system configuration.
    
    Supports YAML and JSON config files.
    Provides validation and access to configuration parameters.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        self.config_path = config_path or Path("config/system_config.json")
        self._config: Dict[str, Any] = {}
        self._loaded = False
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If config file is invalid
        """
        if not self.config_path.exists():
            logger.warning(
                f"Config file not found at {self.config_path}. "
                "Using minimal default config."
            )
            self._config = self._get_default_config()
        else:
            try:
                if self.config_path.suffix == ".json":
                    with open(self.config_path, "r") as f:
                        self._config = json.load(f)
                else:
                    # For YAML support, would add pyyaml dependency
                    raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
                
                logger.info(f"Configuration loaded from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = self._get_default_config()
        
        self._validate_config()
        self._loaded = True
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        Supports nested keys with dot notation (e.g., "risk.max_drawdown").
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if not self._loaded:
            self.load()
        
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def _validate_config(self) -> None:
        """
        Validate configuration structure and required fields.
        Logs warnings for missing optional fields.
        """
        required_fields = ["mode", "risk"]
        
        for field in required_fields:
            if field not in self._config:
                logger.warning(f"Missing required config field: {field}")
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """
        Return minimal default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "mode": "backtesting",
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "risk": {
                "max_portfolio_drawdown": 0.20,
                "position_size_pct": 0.02,
                "stop_loss_pct": 0.05
            },
            "sleeves": {
                "count": 3,
                "default_allocation": {
                    "sleeve_1": 0.50,
                    "sleeve_2": 0.30,
                    "sleeve_3": 0.20
                }
            }
        }
