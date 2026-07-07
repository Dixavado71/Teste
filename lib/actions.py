"""
Actions - Action objects for dixUIAuto.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from lib.logs import setup_logger

logger = setup_logger("Actions")


class Action(ABC):
    """Base class for all actions."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, engine) -> bool:
        """Execute the action."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class ClickAction(Action):
    """Click action."""
    
    def __init__(self, **criteria):
        super().__init__("click")
        self.criteria = criteria
    
    def execute(self, engine) -> bool:
        element = engine.finder.find_first(**self.criteria)
        if element:
            return engine.clicker.click(element)
        logger.warning(f"ClickAction: Element not found {self.criteria}")
        return False


class InputAction(Action):
    """Text input action."""
    
    def __init__(self, label: str, value: str, field_type: Optional[str] = None):
        super().__init__("input")
        self.label = label
        self.value = value
        self.field_type = field_type
    
    def execute(self, engine) -> bool:
        return engine.form.fill(self.label, self.value, self.field_type)


class WaitAction(Action):
    """Wait action."""
    
    def __init__(self, seconds: float = 1.0):
        super().__init__("wait")
        self.seconds = seconds
    
    def execute(self, engine) -> bool:
        import time
        time.sleep(self.seconds)
        return True


class SwipeAction(Action):
    """Swipe action."""
    
    def __init__(self, direction: str = "down", steps: int = 1):
        super().__init__("swipe")
        self.direction = direction
        self.steps = steps
    
    def execute(self, engine) -> bool:
        return engine.gestures.scroll(self.direction, self.steps)


class ScrollAction(Action):
    """Scroll action."""
    
    def __init__(self, direction: str = "down"):
        super().__init__("scroll")
        self.direction = direction
    
    def execute(self, engine) -> bool:
        return engine.gestures.scroll(self.direction)


class ScreenshotAction(Action):
    """Screenshot action."""
    
    def __init__(self, filename: Optional[str] = None):
        super().__init__("screenshot")
        self.filename = filename
    
    def execute(self, engine) -> bool:
        return engine.take_screenshot(self.filename)


class ShellAction(Action):
    """Shell command action."""
    
    def __init__(self, command: str):
        super().__init__("shell")
        self.command = command
    
    def execute(self, engine) -> bool:
        result = engine.adb.shell(self.command)
        logger.info(f"Shell output: {result[:100]}")
        return True


class OpenAppAction(Action):
    """Open application action."""
    
    def __init__(self, package: str):
        super().__init__("open_app")
        self.package = package
    
    def execute(self, engine) -> bool:
        return engine.adb.start_app(self.package)


class CloseAppAction(Action):
    """Close application action."""
    
    def __init__(self, package: str):
        super().__init__("close_app")
        self.package = package
    
    def execute(self, engine) -> bool:
        return engine.adb.stop_app(self.package)


class BackAction(Action):
    """Back button action."""
    
    def __init__(self):
        super().__init__("back")
    
    def execute(self, engine) -> bool:
        return engine.adb.input_keyevent(4)  # KEYCODE_BACK


class HomeAction(Action):
    """Home button action."""
    
    def __init__(self):
        super().__init__("home")
    
    def execute(self, engine) -> bool:
        return engine.adb.input_keyevent(3)  # KEYCODE_HOME


def create_action(action_dict: Dict[str, Any]) -> Action:
    """
    Factory function to create action from dictionary.
    
    Args:
        action_dict: Dictionary with action type and parameters
        
    Returns:
        Action instance
    """
    action_type = action_dict.get('action', '').lower()
    
    if action_type == 'click':
        # Remove 'action' key and use rest as criteria
        criteria = {k: v for k, v in action_dict.items() if k != 'action'}
        return ClickAction(**criteria)
    
    elif action_type == 'fill':
        return InputAction(
            label=action_dict.get('label', ''),
            value=action_dict.get('value', ''),
            field_type=action_dict.get('type')
        )
    
    elif action_type == 'wait':
        return WaitAction(seconds=action_dict.get('seconds', 1.0))
    
    elif action_type == 'swipe' or action_type == 'scroll':
        return ScrollAction(direction=action_dict.get('direction', 'down'))
    
    elif action_type == 'screenshot':
        return ScreenshotAction(filename=action_dict.get('filename'))
    
    elif action_type == 'shell':
        return ShellAction(command=action_dict.get('command', ''))
    
    elif action_type == 'open' or action_type == 'open_app':
        return OpenAppAction(package=action_dict.get('package', ''))
    
    elif action_type == 'close' or action_type == 'close_app':
        return CloseAppAction(package=action_dict.get('package', ''))
    
    elif action_type == 'back':
        return BackAction()
    
    elif action_type == 'home':
        return HomeAction()
    
    else:
        logger.warning(f"Unknown action type: {action_type}")
        return WaitAction(0)
