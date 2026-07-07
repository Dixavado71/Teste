"""
Configuration settings for dixUIAuto framework.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
FLOWS_DIR = BASE_DIR / "flows"
DUMPS_DIR = BASE_DIR / "dumps"
CACHE_DIR = BASE_DIR / "cache"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# ADB settings
ADB_HOST = "127.0.0.1"
ADB_PORT = 5037
ADB_TIMEOUT = 30  # seconds

# Device settings
DEVICE_CONNECT_TIMEOUT = 10  # seconds
DEVICE_POLL_INTERVAL = 0.5  # seconds

# Cache settings
CACHE_ENABLED = True
CACHE_MAX_AGE = 300  # seconds
CACHE_INVALIDATE_ON_CHANGE = True

# Dumper settings
DUMP_TIMEOUT = 10  # seconds
DUMP_RETRY_COUNT = 3

# Finder settings
FINDER_DEFAULT_TIMEOUT = 10  # seconds
FINDER_POLL_INTERVAL = 0.5  # seconds

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "dixuiauto.log"

# Screenshot settings
SCREENSHOT_ON_ERROR = True
SCREENSHOT_FORMAT = "png"

# Flow execution settings
FLOW_ACTION_DELAY = 0.3  # seconds between actions
FLOW_STEP_TIMEOUT = 30  # seconds per step
