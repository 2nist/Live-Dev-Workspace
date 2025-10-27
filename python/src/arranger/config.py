"""
Configuration management for arranger system
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OSCConfig:
    """OSC communication configuration."""
    m4l_to_backend_port: int = 12000
    backend_to_m4l_port: int = 12001
    abletonosc_port: int = 11000
    host: str = "127.0.0.1"


@dataclass
class ArrangerConfig:
    """Main arranger configuration."""
    osc: OSCConfig
    max_history_size: int = 50
    autosave_enabled: bool = True
    autosave_interval: int = 60  # seconds
    default_tempo: float = 120.0
    default_key: str = "C"
    default_time_signature: tuple = (4, 4)
    
    @classmethod
    def default(cls) -> "ArrangerConfig":
        """Create default configuration."""
        return cls(osc=OSCConfig())


# Global config instance
config = ArrangerConfig.default()
