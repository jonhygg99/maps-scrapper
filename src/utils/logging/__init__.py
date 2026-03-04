"""
Logging System for Application
Provides centralized logging with file and console output

DEPRECATED: This module is deprecated. Please use:
from src.utils.logging import Logger

This file remains for backward compatibility only.
"""

# Import from the new modular logging system
from .manager import Logger

# Re-export for backward compatibility
__all__ = ['Logger']
