"""
Watcher - Observes UI changes and notifies the engine.
"""

import time
from typing import Optional, Callable, List
from lib.logs import setup_logger

logger = setup_logger("Watcher")


class Watcher:
    """
    Watcher - Observes the UI interface for changes.
    
    Monitors:
    - Screen changes
    - XML updates
    - Cache invalidation
    - Notifies Engine of changes
    
    Avoids unnecessary polling loops.
    """
    
    def __init__(self, get_xml_callable: Callable[[], str],
                 get_checksum_callable: Callable[[], Optional[str]]):
        """
        Initialize Watcher.
        
        Args:
            get_xml_callable: Callable that returns current XML
            get_checksum_callable: Callable that returns current checksum
        """
        self._get_xml = get_xml_callable
        self._get_checksum = get_checksum_callable
        self._last_checksum: Optional[str] = None
        self._observers: List[Callable[[str], None]] = []
        self._running = False
        self._screen_changed = False
    
    def add_observer(self, callback: Callable[[str], None]) -> None:
        """
        Add an observer to be notified of screen changes.
        
        Args:
            callback: Function to call when screen changes (receives new checksum)
        """
        self._observers.append(callback)
        logger.debug("Observer added")
    
    def remove_observer(self, callback: Callable[[str], None]) -> None:
        """
        Remove an observer.
        
        Args:
            callback: Observer function to remove
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug("Observer removed")
    
    def check_for_changes(self) -> bool:
        """
        Check if the UI has changed.
        
        Returns:
            True if changes detected, False otherwise
        """
        try:
            current_checksum = self._get_checksum()
            
            if current_checksum is None:
                # No checksum available, force update
                self._last_checksum = None
                return True
            
            if current_checksum != self._last_checksum:
                logger.debug(f"Screen changed: {self._last_checksum[:8] if self._last_checksum else 'None'} -> {current_checksum[:8]}")
                self._last_checksum = current_checksum
                self._screen_changed = True
                self._notify_observers(current_checksum)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for changes: {e}")
            return True
    
    def _notify_observers(self, checksum: str) -> None:
        """Notify all observers of a change."""
        for observer in self._observers:
            try:
                observer(checksum)
            except Exception as e:
                logger.error(f"Observer callback failed: {e}")
    
    def wait_for_change(self, timeout: float = 10.0, 
                        poll_interval: float = 0.5) -> bool:
        """
        Wait for a screen change.
        
        Args:
            timeout: Maximum time to wait in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            True if change detected, False if timeout
        """
        start_time = time.time()
        initial_checksum = self._get_checksum()
        
        while time.time() - start_time < timeout:
            current_checksum = self._get_checksum()
            
            if current_checksum != initial_checksum:
                logger.info("Screen change detected")
                return True
            
            time.sleep(poll_interval)
        
        logger.warning("Timeout waiting for screen change")
        return False
    
    def wait_for_stable(self, stable_time: float = 1.0,
                        max_wait: float = 10.0,
                        poll_interval: float = 0.3) -> bool:
        """
        Wait for the screen to become stable (no changes).
        
        Args:
            stable_time: Time without changes to consider stable
            max_wait: Maximum time to wait
            poll_interval: Polling interval
            
        Returns:
            True if screen became stable, False if timeout
        """
        start_time = time.time()
        last_change = time.time()
        
        while time.time() - start_time < max_wait:
            if self.check_for_changes():
                last_change = time.time()
            
            if time.time() - last_change >= stable_time:
                logger.info(f"Screen stable after {time.time() - start_time:.2f}s")
                return True
            
            time.sleep(poll_interval)
        
        logger.warning("Timeout waiting for stable screen")
        return False
    
    @property
    def has_changed(self) -> bool:
        """Check if screen has changed since last check."""
        return self._screen_changed
    
    def reset_change_flag(self) -> None:
        """Reset the change flag."""
        self._screen_changed = False
    
    def force_change_notification(self) -> None:
        """Force notify all observers of a change."""
        checksum = self._get_checksum()
        if checksum:
            self._last_checksum = checksum
            self._notify_observers(checksum)
