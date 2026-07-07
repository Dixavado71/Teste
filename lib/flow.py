"""
Flow Engine - Executes automation flows from JSON definitions.
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from lib.logs import setup_logger
from lib.exceptions import FlowExecutionError
from lib.actions import create_action
from config.settings import FLOWS_DIR, FLOW_ACTION_DELAY, FLOW_STEP_TIMEOUT

logger = setup_logger("FlowEngine")


class FlowEngine:
    """
    Flow Engine - Executes automation flows defined in JSON.
    
    Example JSON flow:
    ```json
    [
        {"action": "click", "text": "Já tenho uma conta"},
        {"action": "click", "text": "Forma de entrar"},
        {"action": "fill", "label": "Número de CPF", "value": "02959350146"},
        {"action": "fill", "label": "Senha", "value": "123456"},
        {"action": "click", "text": "Entrar"}
    ]
    ```
    """
    
    def __init__(self, engine):
        """
        Initialize FlowEngine.
        
        Args:
            engine: DixEngine instance
        """
        self.engine = engine
        self.flows_dir = FLOWS_DIR
        self.action_delay = FLOW_ACTION_DELAY
        self.step_timeout = FLOW_STEP_TIMEOUT
        
        # Ensure flows directory exists
        self.flows_dir.mkdir(parents=True, exist_ok=True)
    
    def load_flow(self, flow_path: Path) -> List[Dict[str, Any]]:
        """
        Load a flow from JSON file.
        
        Args:
            flow_path: Path to flow JSON file
            
        Returns:
            List of action dictionaries
            
        Raises:
            FlowExecutionError: If loading fails
        """
        try:
            with open(flow_path, 'r', encoding='utf-8') as f:
                flow = json.load(f)
            
            if not isinstance(flow, list):
                raise FlowExecutionError("Flow must be a JSON array")
            
            logger.info(f"Loaded flow from {flow_path} ({len(flow)} steps)")
            return flow
            
        except json.JSONDecodeError as e:
            raise FlowExecutionError(f"Invalid JSON in flow file: {e}")
        except FileNotFoundError:
            raise FlowExecutionError(f"Flow file not found: {flow_path}")
        except Exception as e:
            raise FlowExecutionError(f"Failed to load flow: {e}")
    
    def save_flow(self, flow_name: str, flow: List[Dict[str, Any]]) -> Path:
        """
        Save a flow to JSON file.
        
        Args:
            flow_name: Name for the flow file
            flow: List of action dictionaries
            
        Returns:
            Path to saved file
        """
        flow_path = self.flows_dir / f"{flow_name}.json"
        
        with open(flow_path, 'w', encoding='utf-8') as f:
            json.dump(flow, f, indent=4)
        
        logger.info(f"Saved flow to {flow_path}")
        return flow_path
    
    def execute(self, flow: List[Dict[str, Any]], 
                stop_on_error: bool = True) -> bool:
        """
        Execute a flow.
        
        Args:
            flow: List of action dictionaries
            stop_on_error: If True, stop on first error
            
        Returns:
            True if all actions succeeded (or stop_on_error is False)
            
        Raises:
            FlowExecutionError: If action fails and stop_on_error is True
        """
        logger.info(f"Executing flow with {len(flow)} steps")
        
        success_count = 0
        fail_count = 0
        
        for i, action_dict in enumerate(flow):
            step_num = i + 1
            action_type = action_dict.get('action', 'unknown')
            
            logger.info(f"Step {step_num}/{len(flow)}: {action_type}")
            
            try:
                action = create_action(action_dict)
                success = action.execute(self.engine)
                
                if success:
                    success_count += 1
                    logger.debug(f"Step {step_num} completed successfully")
                else:
                    fail_count += 1
                    logger.warning(f"Step {step_num} returned failure")
                    
                    if stop_on_error:
                        raise FlowExecutionError(
                            f"Action {step_num} ({action_type}) failed")
                
                # Delay between actions
                if i < len(flow) - 1:
                    time.sleep(self.action_delay)
                    
            except FlowExecutionError:
                raise
            except Exception as e:
                fail_count += 1
                logger.error(f"Step {step_num} error: {e}")
                
                if stop_on_error:
                    raise FlowExecutionError(
                        f"Step {step_num} ({action_type}) failed: {e}")
        
        logger.info(f"Flow completed: {success_count} succeeded, {fail_count} failed")
        return fail_count == 0
    
    def execute_file(self, flow_name: str, 
                     stop_on_error: bool = True) -> bool:
        """
        Execute a flow from file.
        
        Args:
            flow_name: Name of flow file (without .json extension)
            stop_on_error: If True, stop on first error
            
        Returns:
            True if flow executed successfully
        """
        flow_path = self.flows_dir / f"{flow_name}.json"
        flow = self.load_flow(flow_path)
        return self.execute(flow, stop_on_error)
    
    def run_from_package(self, package: str, 
                         actions: List[Dict[str, Any]]) -> bool:
        """
        Open an app and execute actions.
        
        Args:
            package: App package name
            actions: List of actions to execute
            
        Returns:
            True if successful
        """
        logger.info(f"Running flow for package: {package}")
        
        # Open app
        if not self.engine.adb.start_app(package):
            raise FlowExecutionError(f"Failed to start app: {package}")
        
        # Wait for app to load
        time.sleep(2)
        
        # Execute actions
        return self.execute(actions)
    
    def create_flow_from_actions(self, *actions) -> List[Dict[str, Any]]:
        """
        Create a flow from action dictionaries.
        
        Args:
            *actions: Variable number of action dictionaries
            
        Returns:
            Flow list
        """
        return list(actions)
    
    # Convenience methods for building flows
    
    def click(self, **criteria) -> Dict[str, Any]:
        """Create a click action dict."""
        return {'action': 'click', **criteria}
    
    def fill(self, label: str, value: str) -> Dict[str, Any]:
        """Create a fill action dict."""
        return {'action': 'fill', 'label': label, 'value': value}
    
    def wait(self, seconds: float = 1.0) -> Dict[str, Any]:
        """Create a wait action dict."""
        return {'action': 'wait', 'seconds': seconds}
    
    def scroll(self, direction: str = 'down') -> Dict[str, Any]:
        """Create a scroll action dict."""
        return {'action': 'scroll', 'direction': direction}
    
    def screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Create a screenshot action dict."""
        return {'action': 'screenshot', 'filename': filename}
    
    def back(self) -> Dict[str, Any]:
        """Create a back action dict."""
        return {'action': 'back'}
    
    def home(self) -> Dict[str, Any]:
        """Create a home action dict."""
        return {'action': 'home'}
