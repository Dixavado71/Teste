"""
Actions - Sistema de ações como objetos
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from lib.logs import logger


class BaseAction(ABC):
    """Classe base para todas as ações."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.log = logger.get_logger("Action")
    
    @abstractmethod
    def execute(self, engine) -> bool:
        """Executa a ação."""
        pass
    
    def __repr__(self):
        return f"<{self.name}>"


class ClickAction(BaseAction):
    """Ação de clique."""
    
    def __init__(self, text: str = None, desc: str = None, 
                 resource_id: str = None, **kwargs):
        super().__init__("Click")
        self.criteria = {"text": text, "desc": desc, "resource_id": resource_id}
        self.criteria = {k: v for k, v in self.criteria.items() if v}
        self.criteria.update(kwargs)
    
    def execute(self, engine) -> bool:
        node = engine.finder.find_first(**self.criteria)
        if node:
            return engine.clicker.click(node)
        self.log.error(f"Elemento não encontrado: {self.criteria}")
        return False


class InputAction(BaseAction):
    """Ação de input de texto."""
    
    def __init__(self, text: str, label: str = None, **kwargs):
        super().__init__("Input")
        self.value = text
        self.label = label
        self.extra = kwargs
    
    def execute(self, engine) -> bool:
        if self.label:
            return engine.form.fill(self.label, self.value)
        return engine.keyboard.send_keys(self.value)


class WaitAction(BaseAction):
    """Ação de espera."""
    
    def __init__(self, seconds: int = 1, text: str = None, **kwargs):
        super().__init__("Wait")
        self.seconds = seconds
        self.wait_for = text
        self.criteria = kwargs
    
    def execute(self, engine) -> bool:
        import time
        if self.wait_for:
            return engine.watcher.wait_for_text(self.wait_for, timeout=self.seconds * 2)
        if self.criteria:
            return engine.watcher.wait_for_element(timeout=self.seconds * 2, **self.criteria)
        time.sleep(self.seconds)
        return True


class SwipeAction(BaseAction):
    """Ação de swipe/scroll."""
    
    def __init__(self, direction: str = "down", steps: int = 1):
        super().__init__("Swipe")
        self.direction = direction
        self.steps = steps
    
    def execute(self, engine) -> bool:
        return engine.gestures.scroll(self.direction, self.steps)


class ScrollAction(BaseAction):
    """Ação de scroll."""
    
    def __init__(self, direction: str = "down"):
        super().__init__("Scroll")
        self.direction = direction
    
    def execute(self, engine) -> bool:
        return engine.gestures.scroll(self.direction)


class ScreenshotAction(BaseAction):
    """Ação de screenshot."""
    
    def __init__(self, filename: str = None):
        super().__init__("Screenshot")
        self.filename = filename
    
    def execute(self, engine) -> bool:
        return engine.take_screenshot(self.filename)


class ShellAction(BaseAction):
    """Ação de comando shell."""
    
    def __init__(self, command: str):
        super().__init__("Shell")
        self.command = command
    
    def execute(self, engine) -> bool:
        result = engine.adb.shell(self.command)
        self.log.info(f"Shell result: {result[:100]}")
        return True


class AssertAction(BaseAction):
    """Ação de assert/validação."""
    
    def __init__(self, text: str = None, exists: bool = True, **kwargs):
        super().__init__("Assert")
        self.text = text
        self.should_exist = exists
        self.criteria = kwargs
    
    def execute(self, engine) -> bool:
        if self.text:
            try:
                node = engine.finder.find_text(self.text)
                return self.should_exist == (node is not None)
            except:
                return not self.should_exist
        return True


class FillAction(BaseAction):
    """Ação de preenchimento de formulário."""
    
    def __init__(self, label: str, value: str):
        super().__init__("Fill")
        self.label = label
        self.value = value
    
    def execute(self, engine) -> bool:
        return engine.form.fill(self.label, self.value)


# Mapeamento de ações
ACTION_MAP = {
    "click": ClickAction,
    "input": InputAction,
    "wait": WaitAction,
    "swipe": SwipeAction,
    "scroll": ScrollAction,
    "screenshot": ScreenshotAction,
    "shell": ShellAction,
    "assert": AssertAction,
    "fill": FillAction,
}


def create_action(action_type: str, **params) -> Optional[BaseAction]:
    """Cria ação pelo tipo."""
    action_class = ACTION_MAP.get(action_type.lower())
    if action_class:
        return action_class(**params)
    return None
