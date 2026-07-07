"""
Models - Data models for UI elements in dixUIAuto framework.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from config.constants import (
    ATTR_TEXT, ATTR_RESOURCE_ID, ATTR_CLASS, ATTR_CONTENT_DESC,
    ATTR_BOUNDS, ATTR_CLICKABLE, ATTR_ENABLED, ATTR_FOCUSABLE
)


@dataclass
class Bounds:
    """Represents element bounds (coordinates)."""
    left: int
    top: int
    right: int
    bottom: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    @property
    def center_x(self) -> int:
        return (self.left + self.right) // 2
    
    @property
    def center_y(self) -> int:
        return (self.top + self.bottom) // 2
    
    @property
    def center(self) -> tuple[int, int]:
        return (self.center_x, self.center_y)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is within these bounds."""
        return (self.left <= x <= self.right and 
                self.top <= y <= self.bottom)
    
    def intersects(self, other: 'Bounds') -> bool:
        """Check if these bounds intersect with another."""
        return not (self.right < other.left or 
                   self.left > other.right or 
                   self.bottom < other.top or 
                   self.top > other.bottom)
    
    @classmethod
    def from_string(cls, bounds_str: str) -> 'Bounds':
        """
        Parse bounds from string format [left,top][right,bottom].
        
        Args:
            bounds_str: String like "[0,100][200,300]"
            
        Returns:
            Bounds instance
        """
        try:
            # Remove brackets and split
            bounds_str = bounds_str.strip('[]')
            parts = bounds_str.split('][')
            if len(parts) != 2:
                raise ValueError(f"Invalid bounds format: {bounds_str}")
            
            left, top = map(int, parts[0].split(','))
            right, bottom = map(int, parts[1].split(','))
            
            return cls(left=left, top=top, right=right, bottom=bottom)
        except Exception as e:
            raise ValueError(f"Failed to parse bounds '{bounds_str}': {e}")


@dataclass
class UIElement:
    """
    Represents a UI element parsed from XML.
    
    Each element contains:
    - text
    - resource-id
    - class
    - content-desc
    - bounds
    - parent reference
    - children list
    - siblings list
    - depth
    - index
    """
    text: Optional[str] = None
    resource_id: Optional[str] = None
    clazz: Optional[str] = None  # Using 'clazz' to avoid conflict with 'class' keyword
    content_desc: Optional[str] = None
    bounds: Optional[Bounds] = None
    checkable: bool = False
    checked: bool = False
    clickable: bool = False
    enabled: bool = True
    focusable: bool = False
    focused: bool = False
    long_clickable: bool = False
    password: bool = False
    scrollable: bool = False
    selected: bool = False
    parent: Optional['UIElement'] = None
    children: List['UIElement'] = field(default_factory=list)
    depth: int = 0
    index: int = 0
    attributes: dict[str, str] = field(default_factory=dict)
    
    @property
    def id(self) -> Optional[str]:
        """Alias for resource_id."""
        return self.resource_id
    
    @property
    def description(self) -> Optional[str]:
        """Alias for content_desc."""
        return self.content_desc
    
    @property
    def is_visible(self) -> bool:
        """Check if element is visible (has valid bounds and enabled)."""
        return (self.enabled and 
                self.bounds is not None and 
                self.bounds.width > 0 and 
                self.bounds.height > 0)
    
    @property
    def is_interactable(self) -> bool:
        """Check if element can be interacted with."""
        return self.is_visible and (self.clickable or self.long_clickable)
    
    def get_text(self) -> str:
        """Get text content, fallback to content-desc if no text."""
        return self.text or self.content_desc or ""
    
    def get_xpath(self) -> str:
        """Generate XPath-like string for this element."""
        parts = []
        current = self
        
        while current is not None:
            part = current.clazz or "node"
            if current.index > 0:
                part += f"[{current.index}]"
            parts.insert(0, part)
            current = current.parent
        
        return "/" + "/".join(parts)
    
    def find_child_by_attribute(self, attr_name: str, attr_value: str) -> Optional['UIElement']:
        """Find a child element by attribute."""
        for child in self.children:
            attr = getattr(child, attr_name.replace('-', '_'), None)
            if attr == attr_value:
                return child
            # Also check in attributes dict
            if attr_name in child.attributes and child.attributes[attr_name] == attr_value:
                return child
        return None
    
    def find_children_by_attribute(self, attr_name: str, attr_value: str) -> List['UIElement']:
        """Find all child elements matching attribute."""
        results = []
        for child in self.children:
            attr = getattr(child, attr_name.replace('-', '_'), None)
            if attr == attr_value:
                results.append(child)
            elif attr_name in child.attributes and child.attributes[attr_name] == attr_value:
                results.append(child)
        return results
    
    def to_dict(self) -> dict[str, Any]:
        """Convert element to dictionary representation."""
        return {
            'text': self.text,
            'resource_id': self.resource_id,
            'class': self.clazz,
            'content_desc': self.content_desc,
            'bounds': str(self.bounds) if self.bounds else None,
            'checkable': self.checkable,
            'checked': self.checked,
            'clickable': self.clickable,
            'enabled': self.enabled,
            'focusable': self.focusable,
            'focused': self.focused,
            'long_clickable': self.long_clickable,
            'password': self.password,
            'scrollable': self.scrollable,
            'selected': self.selected,
            'depth': self.depth,
            'index': self.index,
            'children_count': len(self.children)
        }
    
    def __repr__(self) -> str:
        text_preview = (self.text[:20] + "...") if self.text and len(self.text) > 20 else self.text
        return f"UIElement(class={self.clazz}, text={text_preview}, id={self.resource_id})"


@dataclass
class ScreenInfo:
    """Information about the current screen."""
    package: str
    activity: Optional[str]
    width: int
    height: int
    density: float
    orientation: str  # 'portrait' or 'landscape'
    
    @property
    def center(self) -> tuple[int, int]:
        return (self.width // 2, self.height // 2)
    
    def is_portrait(self) -> bool:
        return self.orientation == 'portrait'
    
    def is_landscape(self) -> bool:
        return self.orientation == 'landscape'
