"""
System core module - initialization, configuration, and management
"""

from src.system.manager import SystemManager
from src.system.config import ConfigLoader

__all__ = ["SystemManager", "ConfigLoader"]
