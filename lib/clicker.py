"""
Click Engine - Executes click actions on UI elements.
"""

import time
from typing import Optional, Tuple
from lib.models import UIElement
from lib.logs import setup_logger
from lib.exceptions import ElementNotClickableError, ElementNotFoundError

logger = setup_logger("ClickEngine")


class ClickEngine:
    """
    Click Engine - Executes various click actions on UI elements.
    
    Supports:
    - click(): Standard click
    - double_click(): Double click
    - long_click(): Long press
    - tap(): Tap at coordinates
    - tap_center(): Tap at element center
    - click_parent(): Click parent element
    - click_nearest(): Click nearest clickable element
    """
    
    def __init__(self, device):
        """
        Initialize ClickEngine.
        
        Args:
            device: Device instance with adb bridge
        """
        self.device = device
        self.adb = device.adb
    
    def click(self, element: UIElement, timeout: float = 0.1) -> bool:
        """
        Click on an element.
        
        Args:
            element: UIElement to click
            timeout: Delay after click in seconds
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ElementNotClickableError: If element is not clickable
        """
        if element.bounds is None:
            raise ElementNotClickableError("Element has no bounds")
        
        if not element.enabled:
            logger.warning(f"Element is not enabled: {element}")
        
        center = element.bounds.center
        logger.info(f"Clicking element at {center}")
        
        success = self.tap(center[0], center[1])
        
        if success:
            time.sleep(timeout)
        
        return success
    
    def click_by_coords(self, x: int, y: int, timeout: float = 0.1) -> bool:
        """
        Click at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            timeout: Delay after click in seconds
            
        Returns:
            True if successful
        """
        logger.info(f"Clicking at coordinates ({x}, {y})")
        success = self.tap(x, y)
        
        if success:
            time.sleep(timeout)
        
        return success
    
    def double_click(self, element: UIElement, interval: float = 0.2) -> bool:
        """
        Double click on an element.
        
        Args:
            element: UIElement to double click
            interval: Time between clicks in seconds
            
        Returns:
            True if successful
        """
        if element.bounds is None:
            raise ElementNotClickableError("Element has no bounds")
        
        center = element.bounds.center
        
        logger.info(f"Double clicking element at {center}")
        
        success1 = self.tap(center[0], center[1])
        time.sleep(interval)
        success2 = self.tap(center[0], center[1])
        
        return success1 and success2
    
    def long_click(self, element: UIElement, duration: float = 1.5) -> bool:
        """
        Long press on an element.
        
        Args:
            element: UIElement to long press
            duration: Duration of press in seconds
            
        Returns:
            True if successful
        """
        if element.bounds is None:
            raise ElementNotClickableError("Element has no bounds")
        
        center = element.bounds.center
        
        logger.info(f"Long clicking element at {center} for {duration}s")
        
        # Use input swipe for long press (same start and end point)
        try:
            cmd = f"input swipe {center[0]} {center[1]} {center[0]} {center[1]} {int(duration * 1000)}"
            self.adb.shell(cmd)
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Long click failed: {e}")
            return False
    
    def tap(self, x: int, y: int) -> bool:
        """
        Tap at specific coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful
        """
        try:
            cmd = f"input tap {x} {y}"
            self.adb.shell(cmd)
            return True
        except Exception as e:
            logger.error(f"Tap failed: {e}")
            return False
    
    def tap_center(self, element: UIElement) -> bool:
        """
        Tap at the center of an element.
        
        Args:
            element: UIElement to tap
            
        Returns:
            True if successful
        """
        if element.bounds is None:
            raise ElementNotClickableError("Element has no bounds")
        
        center = element.bounds.center
        return self.tap(center[0], center[1])
    
    def click_parent(self, element: UIElement) -> bool:
        """
        Click on the first clickable parent of an element.
        
        Args:
            element: UIElement to find clickable parent for
            
        Returns:
            True if successful
            
        Raises:
            ElementNotFoundError: If no clickable parent found
        """
        from lib.locator import Locator
        
        locator = Locator()
        parent = locator.find_clickable_parent(element)
        
        if parent is None:
            raise ElementNotFoundError("No clickable parent found")
        
        logger.info(f"Clicking parent element: {parent}")
        return self.click(parent)
    
    def click_nearest(self, reference: UIElement,
                      candidates: list, **kwargs) -> bool:
        """
        Click on the nearest clickable element from candidates.
        
        Args:
            reference: Reference UIElement
            candidates: List of candidate UIElements
            **kwargs: Additional arguments for click()
            
        Returns:
            True if successful
            
        Raises:
            ElementNotFoundError: If no candidates available
        """
        from lib.locator import Locator
        
        if not candidates:
            raise ElementNotFoundError("No candidates available")
        
        locator = Locator()
        nearest = locator.find_nearest(reference, candidates)
        
        if nearest is None:
            raise ElementNotFoundError("No valid candidate found")
        
        logger.info(f"Clicking nearest element: {nearest}")
        return self.click(nearest, **kwargs)
    
    def click_text(self, text: str, finder) -> bool:
        """
        Find and click element by text.
        
        Args:
            text: Text to search for
            finder: Finder instance
            
        Returns:
            True if successful
            
        Raises:
            ElementNotFoundError: If element not found
        """
        elements = finder.find_text(text)
        if not elements:
            raise ElementNotFoundError(f"Element with text '{text}' not found")
        
        return self.click(elements[0])
    
    def click_desc(self, desc: str, finder) -> bool:
        """
        Find and click element by content description.
        
        Args:
            desc: Content description to search for
            finder: Finder instance
            
        Returns:
            True if successful
            
        Raises:
            ElementNotFoundError: If element not found
        """
        elements = finder.find_desc(desc)
        if not elements:
            raise ElementNotFoundError(f"Element with desc '{desc}' not found")
        
        return self.click(elements[0])
    
    def click_resource(self, resource_id: str, finder) -> bool:
        """
        Find and click element by resource ID.
        
        Args:
            resource_id: Resource ID to search for
            finder: Finder instance
            
        Returns:
            True if successful
            
        Raises:
            ElementNotFoundError: If element not found
        """
        elements = finder.find_resource(resource_id)
        if not elements:
            raise ElementNotFoundError(f"Element with resource-id '{resource_id}' not found")
        
        return self.click(elements[0])
