"""
Finder - Element search system with multiple strategies.
"""

import re
import time
from typing import Optional, List, Callable, Any
from lib.models import UIElement
from lib.logs import setup_logger
from lib.exceptions import ElementNotFoundError
from config.settings import FINDER_DEFAULT_TIMEOUT, FINDER_POLL_INTERVAL

logger = setup_logger("Finder")


class Finder:
    """
    Finder - System responsible for element research with multiple strategies.
    
    Provides methods:
    - find_text(): Find by text content
    - find_desc(): Find by content description
    - find_resource(): Find by resource ID
    - find_class(): Find by class name
    - find_xpath(): Find by XPath-like expression
    - find_regex(): Find by regular expression
    - find_multiple(): Find elements matching multiple criteria
    - find_first(): Find first matching element
    - find_visible(): Find visible elements only
    - find_clickable(): Find clickable elements only
    """
    
    def __init__(self, get_root_callable: Callable[[], Optional[UIElement]],
                 timeout: int = FINDER_DEFAULT_TIMEOUT,
                 poll_interval: float = FINDER_POLL_INTERVAL):
        """
        Initialize Finder.
        
        Args:
            get_root_callable: Callable that returns current root UIElement
            timeout: Default timeout for finding elements
            poll_interval: Interval between polling attempts
        """
        self._get_root = get_root_callable
        self._timeout = timeout
        self._poll_interval = poll_interval
    
    def _wait_for_elements(self, finder_func: Callable[[], List[UIElement]], 
                           timeout: Optional[int] = None) -> List[UIElement]:
        """
        Wait for elements to be found with timeout and polling.
        
        Args:
            finder_func: Function that returns list of elements
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            List of found UIElements
        """
        timeout = timeout or self._timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            root = self._get_root()
            if root is not None:
                results = finder_func()
                if results:
                    return results
            
            time.sleep(self._poll_interval)
        
        return []
    
    def find_text(self, text: str, exact: bool = True, 
                  timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by text content.
        
        Args:
            text: Text to search for
            exact: If True, match exactly; if False, match substring
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            from lib.parser import XMLParser
            parser = XMLParser()
            # Re-parse to get fresh data
            return parser.find_by_text(text, exact)
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) with text '{text}'")
        return results
    
    def find_desc(self, desc: str, exact: bool = True,
                  timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by content description.
        
        Args:
            desc: Content description to search for
            exact: If True, match exactly; if False, match substring
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            for element in self._collect_elements(root):
                if element.content_desc:
                    if exact:
                        if element.content_desc == desc:
                            results.append(element)
                    else:
                        if desc in element.content_desc:
                            results.append(element)
            return results
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) with desc '{desc}'")
        return results
    
    def find_resource(self, resource_id: str,
                      timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by resource ID.
        
        Args:
            resource_id: Resource ID to search for
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            for element in self._collect_elements(root):
                if element.resource_id == resource_id:
                    results.append(element)
            return results
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) with resource-id '{resource_id}'")
        return results
    
    def find_class(self, clazz: str,
                   timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by class name.
        
        Args:
            clazz: Class name to search for
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            for element in self._collect_elements(root):
                if element.clazz == clazz:
                    results.append(element)
            return results
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) with class '{clazz}'")
        return results
    
    def find_xpath(self, xpath: str,
                   timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by XPath-like expression.
        
        Args:
            xpath: XPath expression (simplified support)
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        # Simplified XPath implementation
        # Supports: //ClassName[@attribute='value']
        
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            all_elements = self._collect_elements(root)
            
            # Parse simple XPath
            pattern = r'//(\w+)?(?:\[@(\w+)=[\'"]([^\'"]+)[\'"]\])?'
            match = re.match(pattern, xpath)
            
            if not match:
                # Return all if no valid pattern
                return all_elements
            
            class_name = match.group(1)
            attr_name = match.group(2)
            attr_value = match.group(3)
            
            for element in all_elements:
                # Check class
                if class_name and element.clazz != class_name:
                    continue
                
                # Check attribute
                if attr_name and attr_value:
                    attr = getattr(element, attr_name.replace('-', '_'), None)
                    if attr != attr_value:
                        # Also check in attributes dict
                        if attr_name not in element.attributes or \
                           element.attributes[attr_name] != attr_value:
                            continue
                
                results.append(element)
            
            return results
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) with xpath '{xpath}'")
        return results
    
    def find_regex(self, pattern: str, attribute: str = 'text',
                   timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find elements by regular expression on an attribute.
        
        Args:
            pattern: Regular expression pattern
            attribute: Attribute to match against ('text', 'content_desc', 'resource_id')
            timeout: Timeout in seconds
            
        Returns:
            List of matching UIElements
        """
        regex = re.compile(pattern)
        
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            for element in self._collect_elements(root):
                value = getattr(element, attribute.replace('-', '_'), None)
                if value and regex.search(value):
                    results.append(element)
            return results
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} element(s) matching regex '{pattern}' on '{attribute}'")
        return results
    
    def find_multiple(self, **criteria) -> List[UIElement]:
        """
        Find elements matching multiple criteria.
        
        Args:
            **criteria: Key-value pairs of attributes to match
                       e.g., text="Login", clickable=True, class="android.widget.Button"
            
        Returns:
            List of matching UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            
            results = []
            for element in self._collect_elements(root):
                match = True
                for key, value in criteria.items():
                    elem_attr = getattr(element, key.replace('-', '_'), None)
                    if elem_attr != value:
                        match = False
                        break
                if match:
                    results.append(element)
            return results
        
        criteria_str = ", ".join(f"{k}={v}" for k, v in criteria.items())
        results = self._wait_for_elements(finder)
        logger.debug(f"Found {len(results)} element(s) matching: {criteria_str}")
        return results
    
    def find_first(self, **criteria) -> Optional[UIElement]:
        """
        Find the first element matching criteria.
        
        Args:
            **criteria: Key-value pairs of attributes to match
            
        Returns:
            First matching UIElement or None
        """
        results = self.find_multiple(**criteria)
        return results[0] if results else None
    
    def find_visible(self, timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find all visible elements.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            List of visible UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            return [e for e in self._collect_elements(root) if e.is_visible]
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} visible element(s)")
        return results
    
    def find_clickable(self, timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find all clickable elements.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            List of clickable UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            return [e for e in self._collect_elements(root) if e.clickable]
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} clickable element(s)")
        return results
    
    def find_edit_text(self, timeout: Optional[int] = None) -> List[UIElement]:
        """
        Find all EditText (input field) elements.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            List of EditText UIElements
        """
        def finder():
            root = self._get_root()
            if not root:
                return []
            return [e for e in self._collect_elements(root) 
                    if e.clazz and 'EditText' in e.clazz]
        
        results = self._wait_for_elements(finder, timeout)
        logger.debug(f"Found {len(results)} EditText element(s)")
        return results
    
    def _collect_elements(self, root: UIElement) -> List[UIElement]:
        """Collect all elements from tree."""
        elements = []
        
        def traverse(element: UIElement):
            elements.append(element)
            for child in element.children:
                traverse(child)
        
        traverse(root)
        return elements
    
    def ensure_element(self, **criteria) -> UIElement:
        """
        Find an element or raise exception if not found.
        
        Args:
            **criteria: Search criteria
            
        Returns:
            Found UIElement
            
        Raises:
            ElementNotFoundError: If element not found within timeout
        """
        result = self.find_first(**criteria)
        if result is None:
            criteria_str = ", ".join(f"{k}={v}" for k, v in criteria.items())
            raise ElementNotFoundError(f"Element not found: {criteria_str}")
        return result
