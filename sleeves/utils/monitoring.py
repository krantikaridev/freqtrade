"""
Logging and Monitoring utilities for the Hybrid Sleeve system.

Provides structured logging with JSON output for easy parsing and integration
with monitoring systems.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger


class HybridSleeveFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for hybrid sleeve logs."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, 
                   message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log records."""
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name


def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/hybrid_sleeve.log') -> None:
    """
    Configure structured logging for the system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    formatter = HybridSleeveFormatter()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with JSON formatting
    try:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {e}")


class HealthMonitor:
    """
    Basic health monitoring hooks for the trading system.
    
    This foundation class can be extended to:
    - Track system health metrics
    - Monitor API connectivity
    - Log trade execution health
    - Alert on critical issues
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.health_checks: Dict[str, bool] = {}
    
    def register_health_check(self, check_name: str, status: bool) -> None:
        """
        Register a health check result.
        
        Args:
            check_name: Name of the health check
            status: True if healthy, False otherwise
        """
        self.health_checks[check_name] = status
        if not status:
            self.logger.warning(f"Health check failed: {check_name}")
    
    def get_health_status(self) -> bool:
        """
        Get overall system health.
        
        Returns:
            True if all checks pass, False otherwise
        """
        return all(self.health_checks.values())
    
    def log_trade_execution(self, sleeve_id: str, symbol: str, side: str, 
                           amount: float, price: float) -> None:
        """
        Log a trade execution event.
        
        Args:
            sleeve_id: Identifier of the sleeve executing the trade
            symbol: Trading pair symbol
            side: 'buy' or 'sell'
            amount: Trade amount
            price: Execution price
        """
        self.logger.info(
            f"Trade executed",
            extra={
                'sleeve_id': sleeve_id,
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price
            }
        )
