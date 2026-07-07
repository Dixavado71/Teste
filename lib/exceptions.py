"""
Custom exceptions for dixUIAuto framework.
"""


class DixUIAutoError(Exception):
    """Base exception for dixUIAuto framework."""
    pass


class DeviceNotFoundError(DixUIAutoError):
    """Raised when no Android device is found."""
    pass


class DeviceConnectionError(DixUIAutoError):
    """Raised when device connection fails."""
    pass


class ADBCommandError(DixUIAutoError):
    """Raised when an ADB command fails."""
    pass


class ElementNotFoundError(DixUIAutoError):
    """Raised when a UI element cannot be found."""
    pass


class ElementNotClickableError(DixUIAutoError):
    """Raised when a UI element is not clickable."""
    pass


class ElementNotVisibleError(DixUIAutoError):
    """Raised when a UI element is not visible."""
    pass


class AppNotFoundError(DixUIAutoError):
    """Raised when an application is not found on the device."""
    pass


class FlowExecutionError(DixUIAutoError):
    """Raised when a flow execution fails."""
    pass


class CacheError(DixUIAutoError):
    """Raised when cache operations fail."""
    pass


class ParserError(DixUIAutoError):
    """Raised when XML parsing fails."""
    pass


class FormFillError(DixUIAutoError):
    """Raised when form filling fails."""
    pass


class TimeoutError(DixUIAutoError):
    """Raised when an operation times out."""
    pass
