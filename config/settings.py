"""
Configuration settings for dixUIAuto framework.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Settings:
    """Settings dataclass for type-safe configuration."""
    
    # Base directories
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    FLOWS_DIR: Optional[Path] = None
    DUMPS_DIR: Optional[Path] = None
    CACHE_DIR: Optional[Path] = None
    SCREENSHOTS_DIR: Optional[Path] = None
    
    # ADB settings
    ADB_HOST: str = "127.0.0.1"
    ADB_PORT: int = 5037
    ADB_TIMEOUT: int = 30  # seconds
    
    # Device settings
    DEVICE_CONNECT_TIMEOUT: int = 10  # seconds
    DEVICE_POLL_INTERVAL: float = 0.5  # seconds
    
    # Cache settings
    CACHE_ENABLED: bool = True
    CACHE_MAX_AGE: int = 300  # seconds
    CACHE_INVALIDATE_ON_CHANGE: bool = True
    
    # Dumper settings
    DUMP_TIMEOUT: int = 10  # seconds
    DUMP_RETRY_COUNT: int = 3
    
    # Finder settings
    FINDER_DEFAULT_TIMEOUT: int = 10  # seconds
    FINDER_POLL_INTERVAL: float = 0.5  # seconds
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[Path] = None
    
    # Screenshot settings
    SCREENSHOT_ON_ERROR: bool = True
    SCREENSHOT_FORMAT: str = "png"
    
    # Flow execution settings
    FLOW_ACTION_DELAY: float = 0.3  # seconds between actions
    FLOW_STEP_TIMEOUT: int = 30  # seconds per step
    
    # GUI settings
    GUI_THEME: str = "dark-blue"
    GUI_REFRESH_INTERVAL: int = 5  # seconds
    
    def __post_init__(self):
        """Initialize derived paths."""
        if self.FLOWS_DIR is None:
            self.FLOWS_DIR = self.BASE_DIR / "flows"
        if self.DUMPS_DIR is None:
            self.DUMPS_DIR = self.BASE_DIR / "dumps"
        if self.CACHE_DIR is None:
            self.CACHE_DIR = self.BASE_DIR / "cache"
        if self.SCREENSHOTS_DIR is None:
            self.SCREENSHOTS_DIR = self.BASE_DIR / "screenshots"
        if self.LOG_FILE is None:
            self.LOG_FILE = self.BASE_DIR / "dixuiauto.log"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'BASE_DIR': str(self.BASE_DIR),
            'FLOWS_DIR': str(self.FLOWS_DIR),
            'DUMPS_DIR': str(self.DUMPS_DIR),
            'CACHE_DIR': str(self.CACHE_DIR),
            'SCREENSHOTS_DIR': str(self.SCREENSHOTS_DIR),
            'ADB_HOST': self.ADB_HOST,
            'ADB_PORT': self.ADB_PORT,
            'ADB_TIMEOUT': self.ADB_TIMEOUT,
            'DEVICE_CONNECT_TIMEOUT': self.DEVICE_CONNECT_TIMEOUT,
            'DEVICE_POLL_INTERVAL': self.DEVICE_POLL_INTERVAL,
            'CACHE_ENABLED': self.CACHE_ENABLED,
            'CACHE_MAX_AGE': self.CACHE_MAX_AGE,
            'CACHE_INVALIDATE_ON_CHANGE': self.CACHE_INVALIDATE_ON_CHANGE,
            'DUMP_TIMEOUT': self.DUMP_TIMEOUT,
            'DUMP_RETRY_COUNT': self.DUMP_RETRY_COUNT,
            'FINDER_DEFAULT_TIMEOUT': self.FINDER_DEFAULT_TIMEOUT,
            'FINDER_POLL_INTERVAL': self.FINDER_POLL_INTERVAL,
            'LOG_LEVEL': self.LOG_LEVEL,
            'LOG_FORMAT': self.LOG_FORMAT,
            'LOG_FILE': str(self.LOG_FILE),
            'SCREENSHOT_ON_ERROR': self.SCREENSHOT_ON_ERROR,
            'SCREENSHOT_FORMAT': self.SCREENSHOT_FORMAT,
            'FLOW_ACTION_DELAY': self.FLOW_ACTION_DELAY,
            'FLOW_STEP_TIMEOUT': self.FLOW_STEP_TIMEOUT,
            'GUI_THEME': self.GUI_THEME,
            'GUI_REFRESH_INTERVAL': self.GUI_REFRESH_INTERVAL,
        }


# Global settings instance
settings = Settings()

# Legacy constants for backward compatibility
BASE_DIR = settings.BASE_DIR
FLOWS_DIR = settings.FLOWS_DIR
DUMPS_DIR = settings.DUMPS_DIR
CACHE_DIR = settings.CACHE_DIR
SCREENSHOTS_DIR = settings.SCREENSHOTS_DIR
ADB_HOST = settings.ADB_HOST
ADB_PORT = settings.ADB_PORT
ADB_TIMEOUT = settings.ADB_TIMEOUT
DEVICE_CONNECT_TIMEOUT = settings.DEVICE_CONNECT_TIMEOUT
DEVICE_POLL_INTERVAL = settings.DEVICE_POLL_INTERVAL
CACHE_ENABLED = settings.CACHE_ENABLED
CACHE_MAX_AGE = settings.CACHE_MAX_AGE
CACHE_INVALIDATE_ON_CHANGE = settings.CACHE_INVALIDATE_ON_CHANGE
DUMP_TIMEOUT = settings.DUMP_TIMEOUT
DUMP_RETRY_COUNT = settings.DUMP_RETRY_COUNT
FINDER_DEFAULT_TIMEOUT = settings.FINDER_DEFAULT_TIMEOUT
FINDER_POLL_INTERVAL = settings.FINDER_POLL_INTERVAL
LOG_LEVEL = settings.LOG_LEVEL
LOG_FORMAT = settings.LOG_FORMAT
LOG_FILE = settings.LOG_FILE
SCREENSHOT_ON_ERROR = settings.SCREENSHOT_ON_ERROR
SCREENSHOT_FORMAT = settings.SCREENSHOT_FORMAT
FLOW_ACTION_DELAY = settings.FLOW_ACTION_DELAY
FLOW_STEP_TIMEOUT = settings.FLOW_STEP_TIMEOUT
