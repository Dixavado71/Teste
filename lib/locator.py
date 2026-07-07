"""
Locator - Spatial location and element relationship calculations.
"""

import math
from typing import Optional, List, Tuple
from lib.models import UIElement, Bounds
from lib.logs import setup_logger

logger = setup_logger("Locator")


class Locator:
    """
    Locator - Responsible for spatial location calculations.
    
    Calculates:
    - center of elements
    - distance between elements
    - proximity relationships
    - overlaps
    - parent/children/siblings relationships
    
    Allows locating:
    - nearest field
    - nearest button
    - corresponding label
    - clickable container
    """
    
    def __init__(self):
        """Initialize Locator."""
        pass
    
    def get_center(self, element: UIElement) -> Optional[Tuple[int, int]]:
        """
        Get the center coordinates of an element.
        
        Args:
            element: UIElement
            
        Returns:
            (x, y) tuple or None if no bounds
        """
        if element.bounds is None:
            return None
        return element.bounds.center
    
    def get_distance(self, elem1: UIElement, elem2: UIElement) -> float:
        """
        Calculate distance between centers of two elements.
        
        Args:
            elem1: First UIElement
            elem2: Second UIElement
            
        Returns:
            Distance in pixels, or infinity if bounds unavailable
        """
        center1 = self.get_center(elem1)
        center2 = self.get_center(elem2)
        
        if center1 is None or center2 is None:
            return float('inf')
        
        dx = center1[0] - center2[0]
        dy = center1[1] - center2[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def find_nearest(self, reference: UIElement, 
                     candidates: List[UIElement]) -> Optional[UIElement]:
        """
        Find the nearest element from a list of candidates.
        
        Args:
            reference: Reference UIElement
            candidates: List of candidate UIElements
            
        Returns:
            Nearest UIElement or None if no candidates
        """
        if not candidates:
            return None
        
        nearest = None
        min_distance = float('inf')
        
        for candidate in candidates:
            distance = self.get_distance(reference, candidate)
            if distance < min_distance:
                min_distance = distance
                nearest = candidate
        
        return nearest
    
    def find_nearest_by_type(self, reference: UIElement,
                             all_elements: List[UIElement],
                             element_type: str) -> Optional[UIElement]:
        """
        Find nearest element of a specific type.
        
        Args:
            reference: Reference UIElement
            all_elements: List of all UIElements to search
            element_type: Type to filter ('button', 'edittext', 'text', etc.)
            
        Returns:
            Nearest matching UIElement or None
        """
        type_map = {
            'button': lambda e: e.clazz and 'Button' in e.clazz,
            'edittext': lambda e: e.clazz and 'EditText' in e.clazz,
            'text': lambda e: e.clazz and 'TextView' in e.clazz,
            'clickable': lambda e: e.clickable,
            'input': lambda e: e.clazz and 'EditText' in e.clazz,
        }
        
        filter_func = type_map.get(element_type.lower(), lambda e: True)
        candidates = [e for e in all_elements if filter_func(e)]
        
        return self.find_nearest(reference, candidates)
    
    def find_label_for_field(self, field: UIElement,
                              all_elements: List[UIElement],
                              max_distance: float = 200) -> Optional[UIElement]:
        """
        Find a label element associated with an input field.
        
        Searches above and to the left of the field first.
        
        Args:
            field: Input field UIElement
            all_elements: List of all UIElements
            max_distance: Maximum distance to consider
            
        Returns:
            Label UIElement or None
        """
        if field.bounds is None:
            return None
        
        candidates = []
        
        for element in all_elements:
            if element == field:
                continue
            if element.bounds is None:
                continue
            if not element.text:
                continue
            
            # Prefer elements above or to the left
            if element.bounds.bottom <= field.bounds.top or \
               element.bounds.right <= field.bounds.left:
                distance = self.get_distance(field, element)
                if distance < max_distance:
                    candidates.append((distance, element))
        
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        # Fallback to any nearby text
        return self.find_nearest_by_type(field, all_elements, 'text')
    
    def find_field_for_label(self, label: UIElement,
                              all_elements: List[UIElement],
                              max_distance: float = 200) -> Optional[UIElement]:
        """
        Find an input field associated with a label.
        
        Searches below and to the right of the label first.
        
        Args:
            label: Label UIElement
            all_elements: List of all UIElements
            max_distance: Maximum distance to consider
            
        Returns:
            Field UIElement or None
        """
        if label.bounds is None:
            return None
        
        candidates = []
        
        for element in all_elements:
            if element == label:
                continue
            if element.bounds is None:
                continue
            if not (element.clazz and 'EditText' in element.clazz):
                continue
            
            # Prefer elements below or to the right
            if element.bounds.top >= label.bounds.bottom or \
               element.bounds.left >= label.bounds.right:
                distance = self.get_distance(label, element)
                if distance < max_distance:
                    candidates.append((distance, element))
        
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        
        # Fallback to nearest input field
        return self.find_nearest_by_type(label, all_elements, 'edittext')
    
    def check_overlap(self, elem1: UIElement, elem2: UIElement) -> bool:
        """
        Check if two elements overlap.
        
        Args:
            elem1: First UIElement
            elem2: Second UIElement
            
        Returns:
            True if elements overlap
        """
        if elem1.bounds is None or elem2.bounds is None:
            return False
        return elem1.bounds.intersects(elem2.bounds)
    
    def find_overlapping(self, element: UIElement,
                         all_elements: List[UIElement]) -> List[UIElement]:
        """
        Find all elements that overlap with given element.
        
        Args:
            element: Reference UIElement
            all_elements: List of all UIElements
            
        Returns:
            List of overlapping UIElements
        """
        return [e for e in all_elements 
                if e != element and self.check_overlap(element, e)]
    
    def is_above(self, elem1: UIElement, elem2: UIElement) -> bool:
        """Check if elem1 is above elem2."""
        if elem1.bounds is None or elem2.bounds is None:
            return False
        return elem1.bounds.bottom <= elem2.bounds.top
    
    def is_below(self, elem1: UIElement, elem2: UIElement) -> bool:
        """Check if elem1 is below elem2."""
        if elem1.bounds is None or elem2.bounds is None:
            return False
        return elem1.bounds.top >= elem2.bounds.bottom
    
    def is_left_of(self, elem1: UIElement, elem2: UIElement) -> bool:
        """Check if elem1 is to the left of elem2."""
        if elem1.bounds is None or elem2.bounds is None:
            return False
        return elem1.bounds.right <= elem2.bounds.left
    
    def is_right_of(self, elem1: UIElement, elem2: UIElement) -> bool:
        """Check if elem1 is to the right of elem2."""
        if elem1.bounds is None or elem2.bounds is None:
            return False
        return elem1.bounds.left >= elem2.bounds.right
    
    def find_clickable_parent(self, element: UIElement) -> Optional[UIElement]:
        """
        Find the nearest clickable parent element.
        
        Args:
            element: UIElement to start from
            
        Returns:
            Clickable parent UIElement or None
        """
        current = element.parent
        while current is not None:
            if current.clickable:
                return current
            current = current.parent
        return None
    
    def find_children_in_region(self, parent: UIElement,
                                 region: Bounds) -> List[UIElement]:
        """
        Find all children within a specific region.
        
        Args:
            parent: Parent UIElement
            region: Region bounds
            
        Returns:
            List of child UIElements in region
        """
        results = []
        for child in parent.children:
            if child.bounds and child.bounds.intersects(region):
                results.append(child)
        return results
    
    def get_relative_position(self, elem1: UIElement, 
                               elem2: UIElement) -> str:
        """
        Get the relative position of elem1 in relation to elem2.
        
        Args:
            elem1: First UIElement
            elem2: Reference UIElement
            
        Returns:
            String describing position ('above', 'below', 'left', 'right', 'inside')
        """
        if elem1.bounds is None or elem2.bounds is None:
            return 'unknown'
        
        if elem1.bounds.intersects(elem2.bounds):
            return 'inside'
        
        positions = []
        if self.is_above(elem1, elem2):
            positions.append('above')
        if self.is_below(elem1, elem2):
            positions.append('below')
        if self.is_left_of(elem1, elem2):
            positions.append('left')
        if self.is_right_of(elem1, elem2):
            positions.append('right')
        
        return ', '.join(positions) if positions else 'unknown'
