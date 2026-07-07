"""
Device Manager - Handles Android device connections and state.
"""

import time
from typing import Optional, List
from lib.adb_bridge import ADBBridge
from lib.logs import setup_logger
from lib.exceptions import DeviceNotFoundError, DeviceConnectionError
from config.settings import DEVICE_CONNECT_TIMEOUT, DEVICE_POLL_INTERVAL


logger = setup_logger("DeviceManager")


class Device:
    """
    Represents a connected Android device.
    """
    
    def __init__(self, device_id: str, adb: ADBBridge):
        """
        Initialize a Device instance.
        
        Args:
            device_id: The device serial number
            adb: ADBBridge instance
        """
        self.device_id = device_id
        self.adb = adb
        self._screen_on = None
        self._unlocked = None
    
    @property
    def is_connected(self) -> bool:
        """Check if device is still connected."""
        return self.adb.is_device_connected()
    
    def is_screen_on(self) -> bool:
        """
        Check if the device screen is on.
        
        Returns:
            True if screen is on, False otherwise
        """
        output = self.adb.dumpsys("power")
        self._screen_on = "mScreenOn=true" in output or "Display Power: state=ON" in output
        return self._screen_on
    
    def is_locked(self) -> bool:
        """
        Check if the device is locked.
        
        Returns:
            True if device is locked, False otherwise
        """
        output = self.adb.dumpsys("window")
        self._unlocked = "mShowingDream=false" in output and "mDreamingLockscreen=false" in output
        return not self._unlocked
    
    def unlock(self) -> bool:
        """
        Unlock the device if it's locked.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Turn screen on if off
            if not self.is_screen_on():
                self.adb.input_keyevent(224)  # KEYCODE_WAKEUP
                time.sleep(0.5)
            
            # Swipe up or press home to unlock (simple unlock)
            self.adb.input_keyevent(3)  # KEYCODE_HOME
            time.sleep(0.5)
            
            logger.info(f"Device {self.device_id} unlocked")
            return True
        except Exception as e:
            logger.error(f"Failed to unlock device: {e}")
            return False
    
    def turn_screen_on(self) -> bool:
        """
        Turn the device screen on.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_screen_on():
            self.adb.input_keyevent(224)  # KEYCODE_WAKEUP
            logger.info(f"Device {self.device_id} screen turned on")
        return True
    
    def turn_screen_off(self) -> bool:
        """
        Turn the device screen off.
        
        Returns:
            True if successful, False otherwise
        """
        if self.is_screen_on():
            self.adb.input_keyevent(223)  # KEYCODE_SLEEP
            logger.info(f"Device {self.device_id} screen turned off")
        return True
    
    def get_info(self) -> dict:
        """
        Get device information.
        
        Returns:
            Dictionary with device info
        """
        info = {}
        
        # Get Android version
        output = self.adb.shell("getprop ro.build.version.release")
        info['android_version'] = output
        
        # Get SDK version
        output = self.adb.shell("getprop ro.build.version.sdk")
        info['sdk_version'] = output
        
        # Get model
        output = self.adb.shell("getprop ro.product.model")
        info['model'] = output
        
        # Get manufacturer
        output = self.adb.shell("getprop ro.product.manufacturer")
        info['manufacturer'] = output
        
        # Get screen resolution
        output = self.adb.shell("wm size")
        info['resolution'] = output
        
        return info
    
    def __repr__(self) -> str:
        return f"Device({self.device_id})"


class DeviceManager:
    """
    Device Manager - Handles discovery, connection, and management of Android devices.
    """
    
    def __init__(self):
        """Initialize DeviceManager."""
        self._devices: dict[str, Device] = {}
        self._current_device: Optional[Device] = None
        self._adb = ADBBridge()
    
    def discover_devices(self) -> List[str]:
        """
        Discover all connected devices.
        
        Returns:
            List of device IDs
        """
        device_ids = self._adb.devices()
        logger.info(f"Discovered {len(device_ids)} device(s)")
        return device_ids
    
    def connect(self, device_id: Optional[str] = None, timeout: int = DEVICE_CONNECT_TIMEOUT) -> Device:
        """
        Connect to a device.
        
        Args:
            device_id: Device ID to connect to. If None, connects to first available device.
            timeout: Connection timeout in seconds
            
        Returns:
            Device instance
            
        Raises:
            DeviceNotFoundError: If no device is found
            DeviceConnectionError: If connection fails
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            device_ids = self.discover_devices()
            
            if not device_ids:
                time.sleep(DEVICE_POLL_INTERVAL)
                continue
            
            if device_id:
                if device_id not in device_ids:
                    time.sleep(DEVICE_POLL_INTERVAL)
                    continue
                target_id = device_id
            else:
                target_id = device_ids[0]
            
            # Create ADB bridge for specific device
            adb = ADBBridge(target_id)
            device = Device(target_id, adb)
            
            self._devices[target_id] = device
            self._current_device = device
            
            logger.info(f"Connected to device: {target_id}")
            return device
        
        raise DeviceConnectionError(f"Failed to connect to device within {timeout} seconds")
    
    def disconnect(self, device_id: Optional[str] = None) -> bool:
        """
        Disconnect from a device.
        
        Args:
            device_id: Device ID to disconnect. If None, disconnects current device.
            
        Returns:
            True if successful, False otherwise
        """
        if device_id:
            if device_id in self._devices:
                del self._devices[device_id]
                if self._current_device and self._current_device.device_id == device_id:
                    self._current_device = None
                logger.info(f"Disconnected from device: {device_id}")
                return True
        else:
            if self._current_device:
                device_id = self._current_device.device_id
                self._current_device = None
                if device_id in self._devices:
                    del self._devices[device_id]
                logger.info(f"Disconnected from device: {device_id}")
                return True
        
        return False
    
    def get_current_device(self) -> Optional[Device]:
        """
        Get the currently selected device.
        
        Returns:
            Current Device instance or None
        """
        return self._current_device
    
    def set_current_device(self, device_id: str) -> bool:
        """
        Set the current device by ID.
        
        Args:
            device_id: Device ID to set as current
            
        Returns:
            True if successful, False otherwise
        """
        if device_id in self._devices:
            self._current_device = self._devices[device_id]
            self._adb = ADBBridge(device_id)
            logger.info(f"Switched to device: {device_id}")
            return True
        
        logger.warning(f"Device {device_id} not found in connected devices")
        return False
    
    def get_all_devices(self) -> List[Device]:
        """
        Get all connected devices.
        
        Returns:
            List of Device instances
        """
        return list(self._devices.values())
    
    def wait_for_device(self, timeout: int = DEVICE_CONNECT_TIMEOUT) -> Device:
        """
        Wait for a device to be connected.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Device instance
            
        Raises:
            DeviceNotFoundError: If no device appears within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            device_ids = self.discover_devices()
            if device_ids:
                return self.connect(device_ids[0])
            time.sleep(DEVICE_POLL_INTERVAL)
        
        raise DeviceNotFoundError("No device found within timeout period")
    
    def reconnect(self, device_id: Optional[str] = None) -> Device:
        """
        Reconnect to a device.
        
        Args:
            device_id: Device ID to reconnect. If None, reconnects current device.
            
        Returns:
            Device instance
            
        Raises:
            DeviceNotFoundError: If device cannot be reconnected
        """
        target_id = device_id or (self._current_device.device_id if self._current_device else None)
        
        if target_id:
            self.disconnect(target_id)
        
        return self.connect(target_id)
