"""
DixEngine - Central engine for dixUIAuto framework.
"""

import time
from pathlib import Path
from typing import Optional, List, Dict, Any

from lib.logs import setup_logger
from lib.exceptions import DixUIAutoError, DeviceNotFoundError
from lib.device import DeviceManager, Device
from lib.adb_bridge import ADBBridge
from lib.cache import CacheEngine
from lib.dumper import XMLDumper
from lib.parser import XMLParser
from lib.finder import Finder
from lib.locator import Locator
from lib.clicker import ClickEngine
from lib.keyboard import KeyboardEngine
from lib.gestures import Gestures
from lib.form import SmartForm
from lib.watcher import Watcher
from lib.validator import Validator
from lib.flow import FlowEngine
from config.settings import SCREENSHOTS_DIR

logger = setup_logger("DixEngine")


class DixEngine:
    """
    DixEngine - Central engine that coordinates all dixUIAuto modules.
    
    Usage:
        engine = DixEngine()
        engine.connect()
        engine.open("com.example.app")
        engine.wait(text="Login")
        engine.click(text="Entrar")
        engine.form.fill(label="CPF", value="02959350146")
    """
    
    def __init__(self):
        """Initialize DixEngine."""
        self._device_manager = DeviceManager()
        self._device: Optional[Device] = None
        self._adb: Optional[ADBBridge] = None
        
        # Core components
        self._cache = CacheEngine()
        self._dumper: Optional[XMLDumper] = None
        self._parser = XMLParser()
        
        # UI components (initialized after connection)
        self._finder: Optional[Finder] = None
        self._locator = Locator()
        self._clicker: Optional[ClickEngine] = None
        self._keyboard: Optional[KeyboardEngine] = None
        self._gestures: Optional[Gestures] = None
        self._form: Optional[SmartForm] = None
        self._watcher: Optional[Watcher] = None
        self._validator: Optional[Validator] = None
        self._flow: Optional[FlowEngine] = None
        
        # State
        self._root_element = None
        self._all_elements: List = []
        self._current_package: Optional[str] = None
        
        logger.info("DixEngine initialized")
    
    @property
    def device(self) -> Optional[Device]:
        """Get current device."""
        return self._device
    
    @property
    def adb(self) -> Optional[ADBBridge]:
        """Get ADB bridge."""
        return self._adb
    
    @property
    def finder(self) -> Optional[Finder]:
        """Get Finder instance."""
        return self._finder
    
    @property
    def clicker(self) -> Optional[ClickEngine]:
        """Get ClickEngine instance."""
        return self._clicker
    
    @property
    def keyboard(self) -> Optional[KeyboardEngine]:
        """Get KeyboardEngine instance."""
        return self._keyboard
    
    @property
    def gestures(self) -> Optional[Gestures]:
        """Get Gestures instance."""
        return self._gestures
    
    @property
    def form(self) -> Optional[SmartForm]:
        """Get SmartForm instance."""
        return self._form
    
    @property
    def flow(self) -> Optional[FlowEngine]:
        """Get FlowEngine instance."""
        return self._flow
    
    def connect(self, device_id: Optional[str] = None, 
                timeout: int = 10) -> 'DixEngine':
        """
        Connect to an Android device.
        
        Args:
            device_id: Device ID (serial number). If None, uses first available.
            timeout: Connection timeout in seconds
            
        Returns:
            Self for method chaining
            
        Raises:
            DeviceNotFoundError: If no device found
        """
        logger.info(f"Connecting to device: {device_id or 'auto'}")
        
        self._device = self._device_manager.connect(device_id, timeout)
        self._adb = ADBBridge(self._device.device_id)
        
        # Initialize components that need ADB
        self._dumper = XMLDumper(self._adb)
        self._clicker = ClickEngine(self._device)
        self._keyboard = KeyboardEngine(self._device)
        self._gestures = Gestures(self._device)
        
        # Initialize finder with callable to get root element
        self._finder = Finder(lambda: self._root_element)
        
        # Initialize form
        self._form = SmartForm(
            finder=self._finder,
            clicker=self._clicker,
            keyboard=self._keyboard,
            validator=None,  # Will set after validator created
            locator=self._locator
        )
        
        # Initialize watcher
        self._watcher = Watcher(
            get_xml_callable=lambda: self._dumper.last_dump or "",
            get_checksum_callable=lambda: self._cache.checksum
        )
        
        # Initialize validator
        self._validator = Validator(self._finder)
        
        # Update form with validator reference
        self._form.validator = self._validator
        
        # Initialize flow engine
        self._flow = FlowEngine(self)
        
        logger.info(f"Connected to device: {self._device.device_id}")
        return self
    
    def disconnect(self) -> None:
        """Disconnect from device."""
        if self._device:
            self._device_manager.disconnect(self._device.device_id)
            self._device = None
            self._adb = None
            logger.info("Disconnected from device")
    
    def open(self, package: str, activity: Optional[str] = None) -> bool:
        """
        Open an application.
        
        Args:
            package: Application package name
            activity: Optional activity name
            
        Returns:
            True if successful
        """
        logger.info(f"Opening app: {package}")
        
        success = self._adb.start_app(package, activity)
        
        if success:
            self._current_package = package
            time.sleep(1)  # Wait for app to start
            self.refresh()
        
        return success
    
    def close(self, package: Optional[str] = None) -> bool:
        """
        Close an application.
        
        Args:
            package: Package name. If None, closes current package.
            
        Returns:
            True if successful
        """
        pkg = package or self._current_package
        
        if not pkg:
            logger.warning("No package specified to close")
            return False
        
        logger.info(f"Closing app: {pkg}")
        success = self._adb.stop_app(pkg)
        
        if success and pkg == self._current_package:
            self._current_package = None
        
        return success
    
    def refresh(self) -> None:
        """
        Refresh the UI tree (dump XML and parse).
        """
        logger.debug("Refreshing UI tree...")
        
        xml_content = self._dumper.dump()
        
        # Check cache
        if not self._cache.has_changed(xml_content):
            logger.debug("Using cached UI tree")
            return
        
        # Parse and update
        self._root_element = self._parser.parse(xml_content)
        self._all_elements = self._parser.get_all_elements()
        
        # Update cache
        self._cache.update(xml_content, parsed_data=self._root_element)
        
        # Update form with current elements
        if self._form:
            self._form.set_elements(self._all_elements)
        
        logger.debug(f"UI tree refreshed ({len(self._all_elements)} elements)")
    
    def wait(self, timeout: int = 10, **criteria) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            timeout: Timeout in seconds
            **criteria: Search criteria (text, resource_id, etc.)
            
        Returns:
            True if element found
        """
        logger.debug(f"Waiting for element: {criteria} (timeout: {timeout}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            self.refresh()
            element = self._finder.find_first(**criteria)
            
            if element:
                logger.info(f"Element found: {criteria}")
                return True
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout waiting for element: {criteria}")
        return False
    
    def click(self, text: Optional[str] = None, 
              desc: Optional[str] = None,
              resource_id: Optional[str] = None,
              **kwargs) -> bool:
        """
        Click on an element.
        
        Args:
            text: Text to search for
            desc: Content description to search for
            resource_id: Resource ID to search for
            **kwargs: Additional search criteria
            
        Returns:
            True if successful
        """
        self.refresh()
        
        criteria = {}
        if text:
            criteria['text'] = text
        if desc:
            criteria['content_desc'] = desc
        if resource_id:
            criteria['resource_id'] = resource_id
        criteria.update(kwargs)
        
        element = self._finder.find_first(**criteria)
        
        if element:
            return self._clicker.click(element)
        
        logger.warning(f"Element not found for click: {criteria}")
        return False
    
    def type(self, text: str) -> bool:
        """
        Type text into the focused field.
        
        Args:
            text: Text to type
            
        Returns:
            True if successful
        """
        return self._keyboard.send_keys(text)
    
    def swipe(self, direction: str = "down", steps: int = 1) -> bool:
        """
        Swipe/scroll on screen.
        
        Args:
            direction: 'up', 'down', 'left', 'right'
            steps: Number of scroll steps
            
        Returns:
            True if successful
        """
        return self._gestures.scroll(direction, steps)
    
    def take_screenshot(self, filename: Optional[str] = None) -> Path:
        """
        Take a screenshot.
        
        Args:
            filename: Optional filename. Auto-generated if None.
            
        Returns:
            Path to screenshot file
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        output_path = SCREENSHOTS_DIR / filename
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        
        self._adb.screencap(str(output_path))
        logger.info(f"Screenshot saved: {output_path}")
        return output_path
    
    def get_current_package(self) -> Optional[str]:
        """Get current foreground package."""
        return self._adb.get_current_package()
    
    def get_elements(self) -> List:
        """Get all UI elements."""
        self.refresh()
        return self._all_elements
    
    def dump_ui(self, save: bool = False) -> str:
        """
        Get current UI XML dump.
        
        Args:
            save: If True, save to file
            
        Returns:
            XML content
        """
        xml = self._dumper.dump()
        
        if save:
            self._dumper.save()
        
        return xml
    
    def unlock_device(self) -> bool:
        """Unlock the device if locked."""
        return self._device.unlock()
    
    def get_device_info(self) -> dict:
        """Get device information."""
        if self._device:
            return self._device.get_info()
        return {}
