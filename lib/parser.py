"""
XML Parser - Transforms XML into navigable UIElement objects.
"""

import xml.etree.ElementTree as ET
from typing import Optional, List
from lib.models import UIElement, Bounds
from lib.logs import setup_logger
from lib.exceptions import ParserError

logger = setup_logger("XMLParser")


class XMLParser:
    """
    XML Parser - Transforms Android UI XML dump into navigable objects.
    
    Each element becomes a UIElement object containing:
    - text, resource-id, class, content-desc
    - bounds (parsed into Bounds object)
    - parent, children, siblings references
    - depth and index
    """
    
    def __init__(self):
        """Initialize XMLParser."""
        self._root: Optional[UIElement] = None
        self._all_elements: List[UIElement] = []
    
    def parse(self, xml_content: str) -> UIElement:
        """
        Parse XML content into UIElement tree.
        
        Args:
            xml_content: Raw XML string from Android device
            
        Returns:
            Root UIElement of the parsed tree
            
        Raises:
            ParserError: If parsing fails
        """
        try:
            logger.debug("Starting XML parsing...")
            
            # Clean up XML if needed (some dumps have issues)
            xml_content = self._clean_xml(xml_content)
            
            # Parse XML
            root_element = ET.fromstring(xml_content)
            
            # Convert to UIElement tree
            self._root = self._parse_element(root_element, None, 0)
            
            # Build flat list of all elements for quick searching
            self._all_elements = self._collect_all_elements(self._root)
            
            logger.info(f"Parsed {len(self._all_elements)} elements")
            return self._root
            
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            raise ParserError(f"Failed to parse XML: {e}")
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise ParserError(f"Unexpected parsing error: {e}")
    
    def _clean_xml(self, xml_content: str) -> str:
        """
        Clean up XML content for parsing.
        
        Args:
            xml_content: Raw XML string
            
        Returns:
            Cleaned XML string
        """
        # Remove BOM if present
        if xml_content.startswith('\ufeff'):
            xml_content = xml_content[1:]
        
        # Some Android dumps have issues with certain characters
        # Add any necessary cleaning here
        
        return xml_content
    
    def _parse_element(self, element: ET.Element, parent: Optional[UIElement], 
                       depth: int) -> UIElement:
        """
        Parse a single XML element into UIElement.
        
        Args:
            element: XML Element
            parent: Parent UIElement (None for root)
            depth: Depth in the tree
            
        Returns:
            Parsed UIElement
        """
        ui_element = UIElement(
            text=element.get('text'),
            resource_id=element.get('resource-id'),
            clazz=element.get('class'),
            content_desc=element.get('content-desc'),
            parent=parent,
            depth=depth,
            checkable=self._bool_attr(element.get('checkable')),
            checked=self._bool_attr(element.get('checked')),
            clickable=self._bool_attr(element.get('clickable')),
            enabled=self._bool_attr(element.get('enabled', 'true')),
            focusable=self._bool_attr(element.get('focusable')),
            focused=self._bool_attr(element.get('focused')),
            long_clickable=self._bool_attr(element.get('long-clickable')),
            password=self._bool_attr(element.get('password')),
            scrollable=self._bool_attr(element.get('scrollable')),
            selected=self._bool_attr(element.get('selected'))
        )
        
        # Parse bounds
        bounds_str = element.get('bounds')
        if bounds_str:
            try:
                ui_element.bounds = Bounds.from_string(bounds_str)
            except ValueError as e:
                logger.warning(f"Invalid bounds '{bounds_str}': {e}")
        
        # Store all attributes
        ui_element.attributes = dict(element.attrib)
        
        # Parse children
        for index, child_element in enumerate(element):
            child_ui = self._parse_element(child_element, ui_element, depth + 1)
            child_ui.index = index
            ui_element.children.append(child_ui)
        
        return ui_element
    
    def _bool_attr(self, value: Optional[str]) -> bool:
        """Convert string attribute to boolean."""
        if value is None:
            return False
        return value.lower() == 'true'
    
    def _collect_all_elements(self, root: UIElement) -> List[UIElement]:
        """
        Collect all elements in a flat list for quick searching.
        
        Args:
            root: Root UIElement
            
        Returns:
            List of all UIElements
        """
        elements = []
        
        def traverse(element: UIElement):
            elements.append(element)
            for child in element.children:
                traverse(child)
        
        traverse(root)
        return elements
    
    def get_root(self) -> Optional[UIElement]:
        """Get the root element of parsed tree."""
        return self._root
    
    def get_all_elements(self) -> List[UIElement]:
        """Get all elements in the tree."""
        return self._all_elements
    
    def find_by_resource_id(self, resource_id: str) -> List[UIElement]:
        """
        Find elements by resource ID.
        
        Args:
            resource_id: Resource ID to search for
            
        Returns:
            List of matching UIElements
        """
        return [e for e in self._all_elements if e.resource_id == resource_id]
    
    def find_by_text(self, text: str, exact: bool = True) -> List[UIElement]:
        """
        Find elements by text.
        
        Args:
            text: Text to search for
            exact: If True, match exactly; if False, match substring
            
        Returns:
            List of matching UIElements
        """
        results = []
        for element in self._all_elements:
            if element.text:
                if exact:
                    if element.text == text:
                        results.append(element)
                else:
                    if text in element.text:
                        results.append(element)
        return results
    
    def find_by_content_desc(self, desc: str, exact: bool = True) -> List[UIElement]:
        """
        Find elements by content description.
        
        Args:
            desc: Content description to search for
            exact: If True, match exactly; if False, match substring
            
        Returns:
            List of matching UIElements
        """
        results = []
        for element in self._all_elements:
            if element.content_desc:
                if exact:
                    if element.content_desc == desc:
                        results.append(element)
                else:
                    if desc in element.content_desc:
                        results.append(element)
        return results
    
    def find_by_class(self, clazz: str) -> List[UIElement]:
        """
        Find elements by class name.
        
        Args:
            clazz: Class name to search for
            
        Returns:
            List of matching UIElements
        """
        return [e for e in self._all_elements if e.clazz == clazz]
    
    def find_clickable(self) -> List[UIElement]:
        """Find all clickable elements."""
        return [e for e in self._all_elements if e.clickable]
    
    def find_visible(self) -> List[UIElement]:
        """Find all visible elements."""
        return [e for e in self._all_elements if e.is_visible]
    
    def find_edit_texts(self) -> List[UIElement]:
        """Find all EditText elements (input fields)."""
        return [e for e in self._all_elements 
                if e.clazz and 'EditText' in e.clazz]
    
    def find_buttons(self) -> List[UIElement]:
        """Find all Button elements."""
        return [e for e in self._all_elements 
                if e.clazz and 'Button' in e.clazz]
    
    def to_dict(self) -> dict:
        """Convert entire tree to dictionary representation."""
        if not self._root:
            return {}
        
        def element_to_dict(element: UIElement) -> dict:
            result = element.to_dict()
            result['children'] = [element_to_dict(c) for c in element.children]
            return result
        
        return element_to_dict(self._root)
