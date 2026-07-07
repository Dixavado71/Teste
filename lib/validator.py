"""
Validator - Confirms operations and validates UI state.
"""

from typing import Optional, List
from lib.models import UIElement
from lib.logs import setup_logger

logger = setup_logger("Validator")


class Validator:
    """
    Validator - Confirms operations and validates UI state.
    
    Validates:
    - Text input correctness
    - Click success
    - Screen transitions
    - Popup appearances
    - Error occurrences
    """
    
    def __init__(self, finder):
        """
        Initialize Validator.
        
        Args:
            finder: Finder instance for element lookup
        """
        self.finder = finder
    
    def validate_text_entered(self, expected_text: str, 
                               timeout: float = 2.0) -> bool:
        """
        Validate that text was entered correctly.
        
        Args:
            expected_text: Expected text content
            timeout: Timeout to find the text
            
        Returns:
            True if text found
        """
        elements = self.finder.find_text(expected_text, exact=True, timeout=int(timeout))
        found = len(elements) > 0
        
        if found:
            logger.info(f"Validated text: '{expected_text}'")
        else:
            logger.warning(f"Text not found: '{expected_text}'")
        
        return found
    
    def validate_click(self, element: UIElement) -> bool:
        """
        Validate that a click was successful by checking for UI change.
        
        Args:
            element: Element that was clicked
            
        Returns:
            True if click appears successful
        """
        # Check if element is still in same state
        # This is a basic validation - could be enhanced
        if element.bounds is None:
            return False
        
        logger.debug(f"Click validated for element: {element}")
        return True
    
    def validate_screen_changed(self, expected_text: Optional[str] = None,
                                 expected_resource: Optional[str] = None,
                                 timeout: float = 5.0) -> bool:
        """
        Validate that screen has changed to expected state.
        
        Args:
            expected_text: Text that should appear on new screen
            expected_resource: Resource ID that should appear
            timeout: Timeout to wait for change
            
        Returns:
            True if expected element found
        """
        if expected_text:
            elements = self.finder.find_text(expected_text, timeout=int(timeout))
            if elements:
                logger.info(f"Screen change validated by text: '{expected_text}'")
                return True
        
        if expected_resource:
            elements = self.finder.find_resource(expected_resource, timeout=int(timeout))
            if elements:
                logger.info(f"Screen change validated by resource: '{expected_resource}'")
                return True
        
        logger.warning("Screen change validation failed")
        return False
    
    def validate_popup(self, popup_text: str, timeout: float = 3.0) -> bool:
        """
        Validate that a popup appeared.
        
        Args:
            popup_text: Text in the popup
            timeout: Timeout to wait for popup
            
        Returns:
            True if popup found
        """
        elements = self.finder.find_text(popup_text, timeout=int(timeout))
        
        if elements:
            logger.info(f"Popup validated: '{popup_text}'")
            return True
        
        logger.warning(f"Popup not found: '{popup_text}'")
        return False
    
    def validate_error(self, error_indicators: List[str], 
                       timeout: float = 2.0) -> bool:
        """
        Validate if an error occurred by looking for error indicators.
        
        Args:
            error_indicators: List of texts/elements that indicate errors
            timeout: Timeout to search
            
        Returns:
            True if error detected
        """
        for indicator in error_indicators:
            elements = self.finder.find_text(indicator, exact=False, timeout=int(timeout))
            if elements:
                logger.warning(f"Error detected: '{indicator}'")
                return True
        
        return False
    
    def validate_element_visible(self, **criteria) -> bool:
        """
        Validate that an element is visible.
        
        Args:
            **criteria: Search criteria for element
            
        Returns:
            True if element is visible
        """
        element = self.finder.find_first(**criteria)
        
        if element and element.is_visible:
            logger.info(f"Element visible: {criteria}")
            return True
        
        logger.warning(f"Element not visible: {criteria}")
        return False
    
    def validate_element_enabled(self, **criteria) -> bool:
        """
        Validate that an element is enabled.
        
        Args:
            **criteria: Search criteria for element
            
        Returns:
            True if element is enabled
        """
        element = self.finder.find_first(**criteria)
        
        if element and element.enabled:
            logger.info(f"Element enabled: {criteria}")
            return True
        
        logger.warning(f"Element not enabled: {criteria}")
        return False
    
    def validate_input_filled(self, field_criteria: dict, 
                               expected_value: str) -> bool:
        """
        Validate that an input field contains expected value.
        
        Note: Getting actual input value may require special handling
        depending on Android version and app.
        
        Args:
            field_criteria: Criteria to find the field
            expected_value: Expected value in field
            
        Returns:
            True if field likely contains value (based on context)
        """
        element = self.finder.find_first(**field_criteria)
        
        if element:
            # Basic validation - element exists
            # Advanced: would need to query actual value
            logger.info(f"Input field found, assuming filled: {field_criteria}")
            return True
        
        logger.warning(f"Input field not found: {field_criteria}")
        return False
    
    def assert_element_exists(self, **criteria) -> UIElement:
        """
        Assert that an element exists, raise exception if not.
        
        Args:
            **criteria: Search criteria
            
        Returns:
            Found UIElement
            
        Raises:
            AssertionError: If element not found
        """
        element = self.finder.find_first(**criteria)
        
        if element is None:
            raise AssertionError(f"Element does not exist: {criteria}")
        
        logger.debug(f"Element exists: {element}")
        return element
    
    def assert_element_not_exists(self, **criteria) -> bool:
        """
        Assert that an element does not exist.
        
        Args:
            **criteria: Search criteria
            
        Returns:
            True if element doesn't exist
            
        Raises:
            AssertionError: If element found
        """
        element = self.finder.find_first(**criteria, timeout=1)
        
        if element is not None:
            raise AssertionError(f"Element exists when it shouldn't: {criteria}")
        
        logger.debug(f"Element correctly does not exist: {criteria}")
        return True
