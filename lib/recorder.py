"""
Flow Recorder - Records user actions and generates flow code.

This module provides utilities for recording automation flows by capturing
actions performed on the device and generating Python code or JSON flows.
"""

import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from lib.logs import setup_logger
from config.settings import FLOWS_DIR

logger = setup_logger("FlowRecorder")


class RecordedAction:
    """Represents a recorded action."""
    
    def __init__(self, action_type: str, **kwargs):
        self.action_type = action_type
        self.params = kwargs
        self.timestamp = time.time()
        self.description = kwargs.get('description', '')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'action': self.action_type,
            **self.params
        }
    
    def to_python_code(self, indent: str = "    ") -> str:
        """Convert to Python FlowBuilder code."""
        if self.action_type == 'click':
            args = ', '.join(f'{k}="{v}"' for k, v in self.params.items() if v)
            return f'{indent}.click({args})'
        
        elif self.action_type == 'fill':
            label = self.params.get('label', '')
            value = self.params.get('value', '')
            field_type = self.params.get('field_type')
            args = f'label="{label}", value="{value}"'
            if field_type:
                args += f', field_type="{field_type}"'
            return f'{indent}.fill({args})'
        
        elif self.action_type == 'wait':
            seconds = self.params.get('seconds', 1.0)
            return f'{indent}.wait({seconds})'
        
        elif self.action_type == 'swipe':
            direction = self.params.get('direction', 'down')
            return f'{indent}.swipe(direction="{direction}")'
        
        elif self.action_type == 'screenshot':
            name = self.params.get('name')
            if name:
                return f'{indent}.screenshot("{name}")'
            return f'{indent}.screenshot()'
        
        elif self.action_type == 'back':
            return f'{indent}.back()'
        
        elif self.action_type == 'home':
            return f'{indent}.home()'
        
        elif self.action_type == 'open_app':
            package = self.params.get('package', '')
            return f'{indent}.open_app("{package}")'
        
        else:
            return f'{indent}# Unknown action: {self.action_type}'


class FlowRecorder:
    """
    Flow Recorder - Records actions and generates flows.
    
    Usage:
        recorder = FlowRecorder(engine)
        recorder.start()
        
        # ... perform actions manually or programmatically ...
        
        recorder.stop()
        recorder.save("my_flow")
        recorder.export_to_python("my_flow.py")
    """
    
    def __init__(self, engine):
        """
        Initialize FlowRecorder.
        
        Args:
            engine: DixEngine instance
        """
        self.engine = engine
        self.actions: List[RecordedAction] = []
        self.is_recording = False
        self.start_time = None
        self._filters: List[Callable[[Dict], bool]] = []
    
    def start(self, clear: bool = True) -> 'FlowRecorder':
        """
        Start recording actions.
        
        Args:
            clear: If True, clear previous recordings
        
        Returns:
            Self for method chaining
        """
        if clear:
            self.actions = []
        
        self.is_recording = True
        self.start_time = time.time()
        logger.info("Flow recording started")
        return self
    
    def stop(self) -> 'FlowRecorder':
        """Stop recording."""
        self.is_recording = False
        duration = time.time() - self.start_time if self.start_time else 0
        logger.info(f"Flow recording stopped ({len(self.actions)} actions, {duration:.2f}s)")
        return self
    
    def record(self, action_type: str, **kwargs) -> 'FlowRecorder':
        """
        Record an action.
        
        Args:
            action_type: Type of action (click, fill, swipe, etc.)
            **kwargs: Action parameters
        
        Returns:
            Self for method chaining
        """
        if not self.is_recording:
            return self
        
        # Apply filters
        action_dict = {'action': action_type, **kwargs}
        for filter_func in self._filters:
            if not filter_func(action_dict):
                return self
        
        action = RecordedAction(action_type, **kwargs)
        self.actions.append(action)
        logger.debug(f"Recorded: {action_type} - {kwargs}")
        return self
    
    def record_click(self, text: Optional[str] = None,
                     desc: Optional[str] = None,
                     resource_id: Optional[str] = None,
                     description: Optional[str] = None) -> 'FlowRecorder':
        """Record a click action."""
        params = {}
        if text:
            params['text'] = text
        if desc:
            params['desc'] = desc
        if resource_id:
            params['resource_id'] = resource_id
        if description:
            params['description'] = description
        return self.record('click', **params)
    
    def record_fill(self, label: str, value: str,
                    field_type: Optional[str] = None) -> 'FlowRecorder':
        """Record a fill action."""
        return self.record('fill', label=label, value=value, field_type=field_type)
    
    def record_wait(self, seconds: float = 1.0) -> 'FlowRecorder':
        """Record a wait action."""
        return self.record('wait', seconds=seconds)
    
    def record_swipe(self, direction: str = 'down') -> 'FlowRecorder':
        """Record a swipe action."""
        return self.record('swipe', direction=direction)
    
    def record_screenshot(self, name: Optional[str] = None) -> 'FlowRecorder':
        """Record a screenshot action."""
        return self.record('screenshot', name=name)
    
    def record_back(self) -> 'FlowRecorder':
        """Record back button press."""
        return self.record('back')
    
    def record_home(self) -> 'FlowRecorder':
        """Record home button press."""
        return self.record('home')
    
    def record_open_app(self, package: str) -> 'FlowRecorder':
        """Record app open action."""
        return self.record('open_app', package=package)
    
    def add_filter(self, filter_func: Callable[[Dict], bool]) -> 'FlowRecorder':
        """
        Add a filter function that determines which actions to record.
        
        Args:
            filter_func: Function that takes action dict and returns True to record
        """
        self._filters.append(filter_func)
        return self
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get recorded actions as list of dictionaries."""
        return [action.to_dict() for action in self.actions]
    
    def build_flow(self) -> List[Dict[str, Any]]:
        """Build flow from recorded actions."""
        return self.get_actions()
    
    def save(self, name: str) -> str:
        """
        Save recorded flow to JSON file.
        
        Args:
            name: Name for the flow file
        
        Returns:
            Path to saved file
        """
        FLOWS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = FLOWS_DIR / f"{name}.json"
        
        flow = self.build_flow()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(flow, f, indent=4)
        
        logger.info(f"Saved recorded flow to {filepath}")
        return str(filepath)
    
    def export_to_python(self, filepath: str,
                         flow_name: Optional[str] = None) -> str:
        """
        Export recorded flow to Python code using FlowBuilder.
        
        Args:
            filepath: Path to Python file
            flow_name: Optional name for the flow variable
        
        Returns:
            Path to saved file
        """
        if flow_name is None:
            flow_name = Path(filepath).stem
        
        lines = [
            '"""',
            f'Auto-generated flow from FlowRecorder',
            f'Generated at: {time.strftime("%Y-%m-%d %H:%M:%S")}',
            '"""',
            '',
            'from lib.flow_builder import flow',
            '',
            f'# Create flow',
            f'{flow_name}_flow = (flow("{flow_name}")',
        ]
        
        for action in self.actions:
            code_line = action.to_python_code()
            lines.append(code_line)
        
        lines.append('    .build())')
        lines.append('')
        lines.append('# Execute flow')
        lines.append('# engine.flow.execute(flow)')
        lines.append('')
        
        content = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Exported flow to Python: {filepath}")
        return filepath
    
    def export_to_markdown(self, filepath: str) -> str:
        """
        Export recorded flow to Markdown documentation.
        
        Args:
            filepath: Path to Markdown file
        
        Returns:
            Path to saved file
        """
        lines = [
            '# Flow Documentation',
            '',
            f'Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            f'Total steps: {len(self.actions)}',
            '',
            '## Steps',
            ''
        ]
        
        for i, action in enumerate(self.actions, 1):
            action_type = action.action_type
            desc = action.description or str(action.params)
            lines.append(f'{i}. **{action_type}**: {desc}')
        
        lines.append('')
        
        content = '\n'.join(lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Exported flow to Markdown: {filepath}")
        return filepath
    
    def clear(self) -> 'FlowRecorder':
        """Clear all recorded actions."""
        self.actions = []
        return self
    
    def summary(self) -> Dict[str, Any]:
        """Get summary of recorded actions."""
        action_counts = {}
        for action in self.actions:
            action_counts[action.action_type] = action_counts.get(action.action_type, 0) + 1
        
        return {
            'total_actions': len(self.actions),
            'action_types': action_counts,
            'duration': time.time() - self.start_time if self.start_time else 0,
            'is_recording': self.is_recording
        }
    
    def print_summary(self) -> None:
        """Print summary of recorded actions."""
        summary = self.summary()
        print(f"\n{'='*50}")
        print(f"Flow Recording Summary")
        print(f"{'='*50}")
        print(f"Total actions: {summary['total_actions']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Recording: {'Yes' if summary['is_recording'] else 'No'}")
        print(f"\nActions by type:")
        for action_type, count in summary['action_types'].items():
            print(f"  - {action_type}: {count}")
        print(f"{'='*50}\n")


def auto_record_wrapper(engine, func, flow_name: str = "auto"):
    """
    Decorator-like function to automatically record actions during function execution.
    
    Usage:
        def my_test_flow(engine):
            engine.click(text="Login")
            engine.fill(label="CPF", value="123")
        
        auto_record_wrapper(engine, my_test_flow, "login_flow")
    """
    recorder = FlowRecorder(engine)
    recorder.start()
    
    try:
        func(engine)
    finally:
        recorder.stop()
        recorder.save(flow_name)
        recorder.print_summary()
    
    return recorder
