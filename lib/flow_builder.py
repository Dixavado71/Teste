"""
Flow Builder - Fluent builder for creating automation flows programmatically.

Provides a fluent interface for building flows without writing JSON manually.
"""

from typing import List, Dict, Any, Optional, Callable
from lib.logs import setup_logger

logger = setup_logger("FlowBuilder")


class FlowStep:
    """Represents a single step in a flow."""
    
    def __init__(self, action_dict: Dict[str, Any]):
        self.action_dict = action_dict
        self._description = action_dict.get('description', '')
        self._on_error = None
        self._retry_count = 0
        self._condition = None
    
    def desc(self, description: str) -> 'FlowStep':
        """Set step description."""
        self._description = description
        self.action_dict['description'] = description
        return self
    
    def on_error(self, handler: str) -> 'FlowStep':
        """
        Set error handler for this step.
        
        Args:
            handler: 'skip', 'abort', 'retry', or callable
        """
        self._on_error = handler
        self.action_dict['on_error'] = handler
        return self
    
    def retry(self, count: int = 3) -> 'FlowStep':
        """Set retry count for this step."""
        self._retry_count = count
        self.action_dict['retry_count'] = count
        return self
    
    def when(self, condition: Callable[[], bool]) -> 'FlowStep':
        """
        Set conditional execution for this step.
        
        Args:
            condition: Callable that returns True to execute step
        """
        self._condition = condition
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.action_dict.copy()


class FlowBuilder:
    """
    Fluent builder for creating automation flows.
    
    Usage:
        flow = (FlowBuilder()
            .open_app("com.example.app")
            .wait_for(text="Login", timeout=5)
            .click(text="Entrar")
            .fill(label="CPF", value="02959350146")
            .fill(label="Senha", value="123456")
            .click(text="Acessar")
            .wait_for(text="Home")
            .screenshot("home_screen")
            .build())
    """
    
    def __init__(self, name: str = "unnamed_flow"):
        """
        Initialize FlowBuilder.
        
        Args:
            name: Name for the flow
        """
        self.name = name
        self.steps: List[FlowStep] = []
        self._metadata: Dict[str, Any] = {}
    
    def _add_step(self, action_dict: Dict[str, Any]) -> 'FlowBuilder':
        """Add a step to the flow."""
        step = FlowStep(action_dict)
        self.steps.append(step)
        return self
    
    def _last_step(self) -> Optional[FlowStep]:
        """Get the last step added."""
        return self.steps[-1] if self.steps else None
    
    # === Application Control ===
    
    def open_app(self, package: str, activity: Optional[str] = None) -> 'FlowBuilder':
        """Open an application."""
        action = {'action': 'open_app', 'package': package}
        if activity:
            action['activity'] = activity
        return self._add_step(action)
    
    def close_app(self, package: str) -> 'FlowBuilder':
        """Close an application."""
        return self._add_step({'action': 'close_app', 'package': package})
    
    def restart_app(self, package: str) -> 'FlowBuilder':
        """Restart an application."""
        return (self
            .close_app(package)
            .wait(0.5)
            .open_app(package))
    
    # === Waiting ===
    
    def wait(self, seconds: float = 1.0) -> 'FlowBuilder':
        """Wait for specified seconds."""
        return self._add_step({'action': 'wait', 'seconds': seconds})
    
    def wait_for(self, text: Optional[str] = None,
                 desc: Optional[str] = None,
                 resource_id: Optional[str] = None,
                 timeout: int = 10) -> 'FlowBuilder':
        """Wait for an element to appear."""
        action = {'action': 'wait_for', 'timeout': timeout}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        if resource_id:
            action['resource_id'] = resource_id
        return self._add_step(action)
    
    def wait_while(self, text: Optional[str] = None,
                   desc: Optional[str] = None,
                   timeout: int = 10) -> 'FlowBuilder':
        """Wait while an element is visible (waits for it to disappear)."""
        action = {'action': 'wait_while', 'timeout': timeout}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        return self._add_step(action)
    
    # === Clicking ===
    
    def click(self, text: Optional[str] = None,
              desc: Optional[str] = None,
              resource_id: Optional[str] = None,
              xpath: Optional[str] = None,
              **kwargs) -> 'FlowBuilder':
        """Click on an element."""
        action = {'action': 'click'}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        if resource_id:
            action['resource_id'] = resource_id
        if xpath:
            action['xpath'] = xpath
        action.update(kwargs)
        return self._add_step(action)
    
    def double_click(self, text: Optional[str] = None,
                     desc: Optional[str] = None,
                     **kwargs) -> 'FlowBuilder':
        """Double click on an element."""
        action = {'action': 'double_click'}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        action.update(kwargs)
        return self._add_step(action)
    
    def long_click(self, text: Optional[str] = None,
                   duration: float = 1.0,
                   **kwargs) -> 'FlowBuilder':
        """Long click on an element."""
        action = {'action': 'long_click', 'duration': duration}
        if text:
            action['text'] = text
        action.update(kwargs)
        return self._add_step(action)
    
    def click_if_exists(self, text: Optional[str] = None,
                        desc: Optional[str] = None,
                        **kwargs) -> 'FlowBuilder':
        """Click only if element exists (doesn't fail if not found)."""
        action = {'action': 'click_if_exists'}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        action.update(kwargs)
        return self._add_step(action)
    
    # === Input ===
    
    def fill(self, label: str, value: str,
             field_type: Optional[str] = None) -> 'FlowBuilder':
        """Fill a form field by label."""
        action = {
            'action': 'fill',
            'label': label,
            'value': value
        }
        if field_type:
            action['field_type'] = field_type
        return self._add_step(action)
    
    def fill_by_id(self, resource_id: str, value: str) -> 'FlowBuilder':
        """Fill a field by resource ID."""
        return self._add_step({
            'action': 'fill_by_id',
            'resource_id': resource_id,
            'value': value
        })
    
    def type_text(self, text: str) -> 'FlowBuilder':
        """Type text into focused field."""
        return self._add_step({'action': 'type', 'text': text})
    
    def clear_field(self) -> 'FlowBuilder':
        """Clear current focused field."""
        return self._add_step({'action': 'clear'})
    
    def paste(self, text: str) -> 'FlowBuilder':
        """Paste text into focused field."""
        return self._add_step({'action': 'paste', 'text': text})
    
    # === Navigation ===
    
    def back(self) -> 'FlowBuilder':
        """Press back button."""
        return self._add_step({'action': 'back'})
    
    def home(self) -> 'FlowBuilder':
        """Press home button."""
        return self._add_step({'action': 'home'})
    
    def recent_apps(self) -> 'FlowBuilder':
        """Open recent apps."""
        return self._add_step({'action': 'recent_apps'})
    
    # === Gestures ===
    
    def swipe(self, direction: str = 'down',
              steps: int = 1) -> 'FlowBuilder':
        """Swipe in a direction."""
        return self._add_step({
            'action': 'swipe',
            'direction': direction,
            'steps': steps
        })
    
    def scroll_to(self, text: str,
                  direction: str = 'down',
                  max_swipes: int = 10) -> 'FlowBuilder':
        """Scroll until finding an element."""
        return self._add_step({
            'action': 'scroll_to',
            'text': text,
            'direction': direction,
            'max_swipes': max_swipes
        })
    
    def pinch(self, scale: float = 0.5) -> 'FlowBuilder':
        """Pinch gesture (zoom out if scale < 1, zoom in if > 1)."""
        return self._add_step({
            'action': 'pinch',
            'scale': scale
        })
    
    # === Validation ===
    
    def assert_exists(self, text: Optional[str] = None,
                      desc: Optional[str] = None,
                      **kwargs) -> 'FlowBuilder':
        """Assert that an element exists."""
        action = {'action': 'assert_exists'}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        action.update(kwargs)
        return self._add_step(action)
    
    def assert_not_exists(self, text: Optional[str] = None,
                          desc: Optional[str] = None,
                          **kwargs) -> 'FlowBuilder':
        """Assert that an element does not exist."""
        action = {'action': 'assert_not_exists'}
        if text:
            action['text'] = text
        if desc:
            action['desc'] = desc
        action.update(kwargs)
        return self._add_step(action)
    
    def assert_text(self, expected: str,
                    actual_element: Optional[Dict] = None) -> 'FlowBuilder':
        """Assert text content of an element."""
        action = {
            'action': 'assert_text',
            'expected': expected
        }
        if actual_element:
            action.update(actual_element)
        return self._add_step(action)
    
    def validate_field(self, label: str,
                       expected_value: str) -> 'FlowBuilder':
        """Validate a filled field."""
        return self._add_step({
            'action': 'validate_field',
            'label': label,
            'expected_value': expected_value
        })
    
    # === Screenshots ===
    
    def screenshot(self, name: Optional[str] = None) -> 'FlowBuilder':
        """Take a screenshot."""
        return self._add_step({
            'action': 'screenshot',
            'name': name
        })
    
    def screenshot_on_error(self, name: str = "error") -> 'FlowBuilder':
        """Configure screenshot on error."""
        self._metadata['screenshot_on_error'] = name
        return self
    
    # === Shell Commands ===
    
    def shell(self, command: str) -> 'FlowBuilder':
        """Execute ADB shell command."""
        return self._add_step({'action': 'shell', 'command': command})
    
    def set_permission(self, permission: str,
                       value: bool = True) -> 'FlowBuilder':
        """Set app permission."""
        return self._add_step({
            'action': 'set_permission',
            'permission': permission,
            'value': value
        })
    
    # === Conditional Logic ===
    
    def if_exists(self, text: Optional[str] = None,
                  desc: Optional[str] = None,
                  **kwargs) -> 'ConditionalBlock':
        """Start a conditional block that executes if element exists."""
        condition = {'type': 'exists'}
        if text:
            condition['text'] = text
        if desc:
            condition['desc'] = desc
        condition.update(kwargs)
        return ConditionalBlock(self, condition)
    
    def if_text_contains(self, text: str, substring: str) -> 'ConditionalBlock':
        """Start a conditional block based on text containing substring."""
        return ConditionalBlock(self, {
            'type': 'text_contains',
            'text': text,
            'substring': substring
        })
    
    # === Loops ===
    
    def loop(self, times: int) -> 'LoopBlock':
        """Start a loop block."""
        return LoopBlock(self, {'type': 'count', 'times': times})
    
    def loop_while(self, condition: Callable[[], bool]) -> 'LoopBlock':
        """Start a loop that runs while condition is true."""
        return LoopBlock(self, {'type': 'while', 'condition': condition})
    
    def foreach(self, items: List[Any],
                variable: str = 'item') -> 'LoopBlock':
        """Start a foreach loop."""
        return LoopBlock(self, {
            'type': 'foreach',
            'items': items,
            'variable': variable
        })
    
    # === Metadata ===
    
    def with_metadata(self, key: str, value: Any) -> 'FlowBuilder':
        """Add metadata to the flow."""
        self._metadata[key] = value
        return self
    
    def with_retry(self, max_retries: int = 3,
                   delay: float = 1.0) -> 'FlowBuilder':
        """Configure flow-level retry."""
        self._metadata['max_retries'] = max_retries
        self._metadata['retry_delay'] = delay
        return self
    
    def with_timeout(self, timeout: int) -> 'FlowBuilder':
        """Set flow timeout."""
        self._metadata['timeout'] = timeout
        return self
    
    # === Building ===
    
    def build(self) -> List[Dict[str, Any]]:
        """Build and return the flow as a list of dictionaries."""
        flow = []
        for step in self.steps:
            step_dict = step.to_dict()
            flow.append(step_dict)
        
        logger.info(f"Built flow '{self.name}' with {len(flow)} steps")
        return flow
    
    def save(self, filepath: Optional[str] = None) -> str:
        """
        Build and save flow to JSON file.
        
        Args:
            filepath: Path to save. If None, saves to flows/{name}.json
        
        Returns:
            Path to saved file
        """
        import json
        from pathlib import Path
        
        flow = self.build()
        
        if filepath is None:
            flows_dir = Path(__file__).parent.parent / 'flows'
            flows_dir.mkdir(parents=True, exist_ok=True)
            filepath = str(flows_dir / f"{self.name}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(flow, f, indent=4)
        
        logger.info(f"Saved flow to {filepath}")
        return filepath
    
    def extend(self, other_flow: List[Dict[str, Any]]) -> 'FlowBuilder':
        """Extend flow with another flow's steps."""
        for step_dict in other_flow:
            self.steps.append(FlowStep(step_dict))
        return self
    
    def insert_common(self, common_name: str) -> 'FlowBuilder':
        """Insert a common flow pattern by name."""
        from lib.flow_templates import get_template
        
        template = get_template(common_name)
        if template:
            self.extend(template)
        else:
            logger.warning(f"Common flow not found: {common_name}")
        return self


class ConditionalBlock:
    """Represents a conditional block in a flow."""
    
    def __init__(self, builder: FlowBuilder, condition: Dict[str, Any]):
        self.builder = builder
        self.condition = condition
        self.then_steps: List[FlowStep] = []
        self.else_steps: List[FlowStep] = []
        self._in_else = False
    
    def then(self, *args, **kwargs) -> 'ConditionalBlock':
        """Add steps to the 'then' block (alias for chaining)."""
        return self
    
    def do(self, *args, **kwargs) -> 'ConditionalBlock':
        """Alias for method chaining."""
        return self
    
    def else_(self) -> 'ConditionalBlock':
        """Switch to adding 'else' steps."""
        self._in_else = True
        return self
    
    def endif(self) -> FlowBuilder:
        """End the conditional block and return to main builder."""
        # Wrap condition block
        condition_step = {
            'action': 'if',
            'condition': self.condition,
            'then': [s.to_dict() for s in self.then_steps],
            'else': [s.to_dict() for s in self.else_steps]
        }
        self.builder.steps.append(FlowStep(condition_step))
        return self.builder
    
    def __getattr__(self, name: str) -> Callable:
        """Delegate flow methods to add steps to this block."""
        def wrapper(*args, **kwargs):
            # Get the corresponding method from FlowBuilder
            method = getattr(FlowBuilder(), name, None)
            if method:
                # Create a temporary builder to get the action dict
                temp_builder = FlowBuilder()
                method.__get__(temp_builder, FlowBuilder)(*args, **kwargs)
                if temp_builder.steps:
                    step = temp_builder.steps[0]
                    if self._in_else:
                        self.else_steps.append(step)
                    else:
                        self.then_steps.append(step)
            return self
        return wrapper


class LoopBlock:
    """Represents a loop block in a flow."""
    
    def __init__(self, builder: FlowBuilder, loop_config: Dict[str, Any]):
        self.builder = builder
        self.loop_config = loop_config
        self.body_steps: List[FlowStep] = []
    
    def do(self, *args, **kwargs) -> 'LoopBlock':
        """Alias for method chaining."""
        return self
    
    def endloop(self) -> FlowBuilder:
        """End the loop block and return to main builder."""
        loop_step = {
            'action': 'loop',
            'config': self.loop_config,
            'body': [s.to_dict() for s in self.body_steps]
        }
        self.builder.steps.append(FlowStep(loop_step))
        return self.builder
    
    def __getattr__(self, name: str) -> Callable:
        """Delegate flow methods to add steps to loop body."""
        def wrapper(*args, **kwargs):
            method = getattr(FlowBuilder(), name, None)
            if method:
                temp_builder = FlowBuilder()
                method.__get__(temp_builder, FlowBuilder)(*args, **kwargs)
                if temp_builder.steps:
                    self.body_steps.append(temp_builder.steps[0])
            return self
        return wrapper


# === Convenience Functions ===

def flow(name: str = "unnamed") -> FlowBuilder:
    """Create a new flow builder."""
    return FlowBuilder(name)


def common_flow(name: str, *args, **kwargs) -> List[Dict[str, Any]]:
    """Get a common flow template by name."""
    from lib.flow_templates import get_template
    return get_template(name, *args, **kwargs)
