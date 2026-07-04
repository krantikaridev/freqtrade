"""
Utility functions for configuration and environment management.
"""

import os
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


def load_environment_config(env: Optional[str] = None) -> Dict[str, Any]:
    """
    Load environment configuration.
    
    Reads from .env file and environment variables.
    Supports dev, staging, and production environments.
    
    Args:
        env: Environment name (dev, staging, prod). If None, reads from ENV variable.
    
    Returns:
        Dictionary of environment configuration
    """
    load_dotenv()
    
    if env is None:
        env = os.getenv('ENVIRONMENT', 'dev')
    
    config = {
        'environment': env,
        'exchange_api_key': os.getenv('EXCHANGE_API_KEY'),
        'exchange_api_secret': os.getenv('EXCHANGE_API_SECRET'),
        'exchange_name': os.getenv('EXCHANGE_NAME', 'binance'),
        'initial_balance': float(os.getenv('INITIAL_BALANCE', 1000)),
        'max_drawdown': float(os.getenv('MAX_PORTFOLIO_DRAWDOWN', 0.20)),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    }
    
    return config


def load_yaml_config(filepath: str) -> Dict[str, Any]:
    """
    Load YAML configuration file.
    
    Args:
        filepath: Path to YAML file
    
    Returns:
        Dictionary representation of YAML
    
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Config file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        config = yaml.safe_load(f)
    
    return config or {}


def interpolate_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively interpolate environment variables in config.
    
    Replaces ${VAR_NAME} with environment variable values.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Configuration with environment variables interpolated
    """
    if isinstance(config, dict):
        return {k: interpolate_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [interpolate_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Replace ${VAR} with environment variable
        import re
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, config)
    else:
        return config
