"""
Gestures - Touch gesture support for dixUIAuto.
"""

import time
from typing import Optional, List, Tuple
from lib.logs import setup_logger

logger = setup_logger("Gestures")


class Gestures:
    """
    Gestures - Support for various touch gestures.
    
    Supports:
    - scroll(): Scroll in a direction
    - fling(): Fast scroll
    - pinch(): Pinch gesture (zoom in/out)
    - zoom(): Zoom gesture
    - drag(): Drag from one point to another
    - multi_touch(): Multi-touch gestures
    - gesture_path(): Execute custom gesture path
    """
    
    def __init__(self, device):
        """
        Initialize Gestures.
        
        Args:
            device: Device instance with adb bridge
        """
        self.device = device
        self.adb = device.adb
        self._screen_width = None
        self._screen_height = None
    
    def _get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        if self._screen_width and self._screen_height:
            return self._screen_width, self._screen_height
        
        output = self.adb.shell("wm size")
        try:
            parts = output.split(":")[1].strip().split("x")
            self._screen_width = int(parts[0])
            self._screen_height = int(parts[1])
        except:
            self._screen_width = 1080
            self._screen_height = 1920
        
        return self._screen_width, self._screen_height
    
    def scroll(self, direction: str = "down", steps: int = 5,
               duration: float = 0.3) -> bool:
        """
        Scroll in a direction.
        
        Args:
            direction: 'up', 'down', 'left', 'right'
            steps: Number of scroll steps
            duration: Duration per step in seconds
            
        Returns:
            True if successful
        """
        width, height = self._get_screen_size()
        
        # Define swipe coordinates based on direction
        swipes = {
            'down': (width // 2, height * 3 // 4, width // 2, height // 4),
            'up': (width // 2, height // 4, width // 2, height * 3 // 4),
            'left': (width * 3 // 4, height // 2, width // 4, height // 2),
            'right': (width // 4, height // 2, width * 3 // 4, height // 2),
        }
        
        if direction not in swipes:
            logger.error(f"Invalid direction: {direction}")
            return False
        
        x1, y1, x2, y2 = swipes[direction]
        
        logger.info(f"Scrolling {direction} ({steps} steps)")
        
        for _ in range(steps):
            success = self.swipe(x1, y1, x2, y2, duration)
            if not success:
                return False
            time.sleep(0.1)
        
        return True
    
    def fling(self, direction: str = "down") -> bool:
        """
        Perform a fast fling gesture.
        
        Args:
            direction: 'up', 'down', 'left', 'right'
            
        Returns:
            True if successful
        """
        return self.scroll(direction, steps=1, duration=0.1)
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int,
              duration: float = 0.5) -> bool:
        """
        Swipe from one point to another.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Swipe duration in seconds
            
        Returns:
            True if successful
        """
        try:
            cmd = f"input swipe {start_x} {start_y} {end_x} {end_y} {int(duration * 1000)}"
            self.adb.shell(cmd)
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"Swipe failed: {e}")
            return False
    
    def pinch(self, scale: float = 0.5, center_x: Optional[int] = None,
              center_y: Optional[int] = None) -> bool:
        """
        Perform pinch gesture (zoom in or out).
        
        Args:
            scale: Scale factor (< 1 for zoom out, > 1 for zoom in)
            center_x: Center X coordinate (default: screen center)
            center_y: Center Y coordinate (default: screen center)
            
        Returns:
            True if successful
        """
        width, height = self._get_screen_size()
        cx = center_x or width // 2
        cy = center_y or height // 2
        
        # Starting distance from center
        start_dist = min(width, height) // 4
        end_dist = int(start_dist * scale)
        
        logger.info(f"Pinching with scale {scale}")
        
        # Simulate two-finger pinch
        if scale < 1:
            # Zoom out - fingers move inward
            self._multi_pinch(cx, cy, start_dist, end_dist)
        else:
            # Zoom in - fingers move outward
            self._multi_pinch(cx, cy, end_dist, start_dist)
        
        return True
    
    def _multi_pinch(self, cx: int, cy: int, start_dist: int, end_dist: int) -> bool:
        """Execute multi-finger pinch gesture."""
        try:
            # Simplified: just do horizontal pinch
            if start_dist > end_dist:
                # Pinch in
                self.adb.shell(f"input swipe {cx - start_dist} {cy} {cx - end_dist} {cy} 200")
                self.adb.shell(f"input swipe {cx + start_dist} {cy} {cx + end_dist} {cy} 200")
            else:
                # Pinch out
                self.adb.shell(f"input swipe {cx - start_dist} {cy} {cx - end_dist} {cy} 200")
                self.adb.shell(f"input swipe {cx + start_dist} {cy} {cx + end_dist} {cy} 200")
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Multi-pinch failed: {e}")
            return False
    
    def zoom(self, factor: float = 1.5) -> bool:
        """
        Zoom in or out.
        
        Args:
            factor: Zoom factor (> 1 for zoom in, < 1 for zoom out)
            
        Returns:
            True if successful
        """
        return self.pinch(scale=1/factor if factor < 1 else factor)
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
             duration: float = 1.0) -> bool:
        """
        Drag from one point to another (longer duration than swipe).
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Drag duration in seconds
            
        Returns:
            True if successful
        """
        logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        return self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def gesture_path(self, points: List[Tuple[int, int]], 
                     total_duration: float = 1.0) -> bool:
        """
        Execute a custom gesture path.
        
        Args:
            points: List of (x, y) coordinates
            total_duration: Total gesture duration in seconds
            
        Returns:
            True if successful
        """
        if len(points) < 2:
            logger.error("Need at least 2 points for gesture path")
            return False
        
        logger.info(f"Executing gesture path with {len(points)} points")
        
        segment_duration = total_duration / (len(points) - 1)
        
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            self.swipe(x1, y1, x2, y2, segment_duration)
        
        return True
    
    def scroll_to_element(self, element, finder, max_swipes: int = 10) -> bool:
        """
        Scroll until an element is visible.
        
        Args:
            element: Element criteria (text, resource_id, etc.)
            finder: Finder instance
            max_swipes: Maximum number of scrolls
            
        Returns:
            True if element found
        """
        for i in range(max_swipes):
            # Check if element exists
            if hasattr(element, 'text') and element.text:
                results = finder.find_text(element.text, timeout=1)
            elif hasattr(element, 'resource_id') and element.resource_id:
                results = finder.find_resource(element.resource_id, timeout=1)
            else:
                results = finder.find_first(**element) if isinstance(element, dict) else []
            
            if results:
                logger.info(f"Element found after {i} swipes")
                return True
            
            # Scroll down
            self.scroll('down', steps=1)
        
        logger.warning(f"Element not found after {max_swipes} swipes")
        return False
