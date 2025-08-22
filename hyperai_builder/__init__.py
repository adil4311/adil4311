"""
HyperAI Builder - Ultra-advanced AI App Builder

A professional-grade application builder that generates fully functional,
deployable AI applications using natural language descriptions.
"""

__version__ = "1.0.0"
__author__ = "HyperAI Team"
__email__ = "team@hyperai.com"

from .core.config import get_settings
from .core.logging import setup_logging

__all__ = ["get_settings", "setup_logging"]