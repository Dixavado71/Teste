"""
dixUIAuto - Android UI Automation Framework

A modular, high-performance Android automation framework built on uiautomator2 and ADB.

Features:
    - Smart Cache: Avoids unnecessary UI dumps by detecting changes
    - Smart Form Filler: Automatically fills forms by identifying fields via labels
    - Advanced Finder: Multiple search strategies (text, ID, content-desc, XPath)
    - Spatial Locator: Position calculations and element relationships
    - Flow Engine: JSON-defined flow execution
    - Smart Inspector: Suggests best selectors with scoring
    - Real-time Watcher: Observes UI changes
    - Robust Validator: Assertions and validations

Basic Usage:
    >>> from lib.engine import DixEngine
    >>> engine = DixEngine()
    >>> engine.connect()
    >>> engine.open("com.example.app")
    >>> engine.click(text="Login")
    >>> engine.form.fill(label="Username", value="user123")
    >>> engine.disconnect()
"""

__version__ = "0.2.0"
__author__ = "dixUIAuto Team"

from lib.exceptions import (
    DixUIAutoError,
    DeviceNotFoundError,
    DeviceConnectionError,
    ADBCommandError,
    ElementNotFoundError,
    ElementNotClickableError,
    ElementNotVisibleError,
    AppNotFoundError,
    FlowExecutionError,
    CacheError,
    ParserError,
    FormFillError,
    TimeoutError,
)

__all__ = [
    "__version__",
    "__author__",
    "DixUIAutoError",
    "DeviceNotFoundError",
    "DeviceConnectionError",
    "ADBCommandError",
    "ElementNotFoundError",
    "ElementNotClickableError",
    "ElementNotVisibleError",
    "AppNotFoundError",
    "FlowExecutionError",
    "CacheError",
    "ParserError",
    "FormFillError",
    "TimeoutError",
]
