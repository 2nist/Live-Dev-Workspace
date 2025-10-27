"""
Live Development Integration Package

Unified Python interface for Ableton Live and Max for Live development,
integrating pylive and AbletonOSC capabilities.
"""

__version__ = "1.0.0"
__author__ = "ALSE Development Team"

from .live_connection import LiveConnection
from .m4l_helpers import M4LDeviceHelper
from .utils import logger, configure_logging

__all__ = [
    "LiveConnection",
    "M4LDeviceHelper",
    "logger",
    "configure_logging",
]
