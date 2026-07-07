"""
ADB Bridge - Abstracts all ADB commands for dixUIAuto framework.
"""

import subprocess
import re
from typing import List, Optional, Tuple
from config.settings import ADB_TIMEOUT
from config.constants import (
    ADB_CMD_DEVICES, ADB_CMD_SHELL, ADB_CMD_INSTALL, ADB_CMD_UNINSTALL,
    ADB_CMD_PULL, ADB_CMD_PUSH, ADB_CMD_START, ADB_CMD_STOP,
    ADB_CMD_SCREENCAP, ADB_CMD_DUMPSYS, ADB_CMD_INPUT
)
from lib.logs import setup_logger
from lib.exceptions import ADBCommandError, DeviceNotFoundError

logger = setup_logger("ADBBridge")


class ADBBridge:
    """
    ADB Bridge class that abstracts all ADB commands.
    
    This class provides a clean interface to execute ADB commands
    and handle responses appropriately.
    """
    
    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADBBridge with optional device ID.
        
        Args:
            device_id: The Android device ID (serial number)
        """
        self.device_id = device_id
        self._adb_path = "adb"
    
    def _run_command(self, command: str, timeout: int = ADB_TIMEOUT) -> Tuple[int, str, str]:
        """
        Run an ADB command and return the result.
        
        Args:
            command: The full ADB command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
            
        Raises:
            ADBCommandError: If command execution fails
        """
        try:
            logger.debug(f"Executing ADB command: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            raise ADBCommandError(f"Command timed out: {command}")
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise ADBCommandError(f"Command execution failed: {e}")
    
    def _build_device_command(self, subcommand: str) -> str:
        """
        Build an ADB command with device specification.
        
        Args:
            subcommand: The ADB subcommand to execute
            
        Returns:
            Full ADB command string
        """
        if self.device_id:
            return f"{self._adb_path} -s {self.device_id} {subcommand}"
        return f"{self._adb_path} {subcommand}"
    
    def devices(self) -> List[str]:
        """
        Get list of connected devices.
        
        Returns:
            List of device IDs
        """
        command = f"{self._adb_path} {ADB_CMD_DEVICES}"
        returncode, stdout, stderr = self._run_command(command)
        
        if returncode != 0:
            logger.error(f"Failed to get devices: {stderr}")
            return []
        
        devices = []
        for line in stdout.strip().split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    devices.append(parts[0])
        
        logger.info(f"Found {len(devices)} device(s): {devices}")
        return devices
    
    def shell(self, command: str) -> str:
        """
        Execute a shell command on the device.
        
        Args:
            command: Shell command to execute
            
        Returns:
            Command output
        """
        full_command = self._build_device_command(f"{ADB_CMD_SHELL} \"{command}\"")
        returncode, stdout, stderr = self._run_command(full_command)
        
        if returncode != 0:
            logger.warning(f"Shell command failed: {stderr}")
        
        return stdout.strip()
    
    def start_app(self, package: str, activity: Optional[str] = None) -> bool:
        """
        Start an application on the device.
        
        Args:
            package: Application package name
            activity: Optional activity name
            
        Returns:
            True if successful, False otherwise
        """
        if activity:
            component = f"{package}/{activity}"
        else:
            # Try to get launch activity
            component = package
        
        command = self._build_device_command(f"{ADB_CMD_START} -n {component}")
        returncode, stdout, stderr = self._run_command(command)
        
        success = returncode == 0 or "Error" not in stderr
        logger.info(f"Started app {package}: {'Success' if success else 'Failed'}")
        return success
    
    def stop_app(self, package: str) -> bool:
        """
        Force stop an application on the device.
        
        Args:
            package: Application package name
            
        Returns:
            True if successful, False otherwise
        """
        command = self._build_device_command(f"{ADB_CMD_STOP} {package}")
        returncode, stdout, stderr = self._run_command(command)
        
        success = returncode == 0
        logger.info(f"Stopped app {package}: {'Success' if success else 'Failed'}")
        return success
    
    def install(self, apk_path: str) -> bool:
        """
        Install an APK on the device.
        
        Args:
            apk_path: Path to the APK file
            
        Returns:
            True if successful, False otherwise
        """
        command = self._build_device_command(f"{ADB_CMD_INSTALL} -r {apk_path}")
        returncode, stdout, stderr = self._run_command(command)
        
        success = "Success" in stdout
        logger.info(f"Installed {apk_path}: {'Success' if success else 'Failed'}")
        return success
    
    def uninstall(self, package: str) -> bool:
        """
        Uninstall an application from the device.
        
        Args:
            package: Application package name
            
        Returns:
            True if successful, False otherwise
        """
        command = self._build_device_command(f"{ADB_CMD_UNINSTALL} {package}")
        returncode, stdout, stderr = self._run_command(command)
        
        success = "Success" in stdout
        logger.info(f"Uninstalled {package}: {'Success' if success else 'Failed'}")
        return success
    
    def pull(self, remote_path: str, local_path: str) -> bool:
        """
        Pull a file from the device.
        
        Args:
            remote_path: Path on the device
            local_path: Local destination path
            
        Returns:
            True if successful, False otherwise
        """
        command = f"{self._adb_path} {ADB_CMD_PULL} {remote_path} {local_path}"
        returncode, stdout, stderr = self._run_command(command)
        
        success = returncode == 0
        logger.info(f"Pulled {remote_path}: {'Success' if success else 'Failed'}")
        return success
    
    def push(self, local_path: str, remote_path: str) -> bool:
        """
        Push a file to the device.
        
        Args:
            local_path: Local source path
            remote_path: Destination path on the device
            
        Returns:
            True if successful, False otherwise
        """
        command = f"{self._adb_path} {ADB_CMD_PUSH} {local_path} {remote_path}"
        returncode, stdout, stderr = self._run_command(command)
        
        success = returncode == 0
        logger.info(f"Pushed {local_path}: {'Success' if success else 'Failed'}")
        return success
    
    def screencap(self, output_path: str) -> bool:
        """
        Capture a screenshot from the device.
        
        Args:
            output_path: Local path to save the screenshot
            
        Returns:
            True if successful, False otherwise
        """
        # Capture to device first, then pull
        temp_path = "/sdcard/screenshot.png"
        shell_cmd = f"{ADB_CMD_SCREENCAP} -p {temp_path}"
        shell_result = self.shell(shell_cmd)
        
        # Pull the screenshot
        success = self.pull(temp_path, output_path)
        
        # Clean up
        self.shell(f"rm {temp_path}")
        
        logger.info(f"Screenshot saved to {output_path}")
        return success
    
    def dumpsys(self, service: str) -> str:
        """
        Get dumpsys output for a specific service.
        
        Args:
            service: Service name to dump
            
        Returns:
            Dumpsys output
        """
        command = self._build_device_command(f"{ADB_CMD_DUMPSYS} {service}")
        returncode, stdout, stderr = self._run_command(command)
        
        return stdout
    
    def input_text(self, text: str) -> bool:
        """
        Input text using ADB input.
        
        Args:
            text: Text to input
            
        Returns:
            True if successful, False otherwise
        """
        # Escape special characters
        escaped_text = text.replace(' ', '%s').replace("'", "\\'")
        command = self._build_device_command(f"{ADB_CMD_INPUT} text '{escaped_text}'")
        returncode, stdout, stderr = self._run_command(command)
        
        return returncode == 0
    
    def input_keyevent(self, keycode: int) -> bool:
        """
        Send a key event to the device.
        
        Args:
            keycode: Android keycode
            
        Returns:
            True if successful, False otherwise
        """
        command = self._build_device_command(f"{ADB_CMD_INPUT} keyevent {keycode}")
        returncode, stdout, stderr = self._run_command(command)
        
        return returncode == 0
    
    def get_current_package(self) -> Optional[str]:
        """
        Get the current foreground application package.
        
        Returns:
            Package name or None if not found
        """
        output = self.dumpsys("window windows")
        
        # Try to find current focused app
        pattern = r'mCurrentFocus=Window\{[^}]+\s([^/\s]+)/([^/\s]+)'
        match = re.search(pattern, output)
        
        if match:
            return match.group(1)
        
        # Alternative method
        output = self.dumpsys("activity activities")
        pattern = r'Recent tasks:\s*\d+:\s*TaskRecord\{[^}]+\s*Intent\s*\{[^}]*\s*([^/\s]+)/([^/\s]+)'
        match = re.search(pattern, output)
        
        if match:
            return match.group(1)
        
        return None
    
    def is_device_connected(self) -> bool:
        """
        Check if the device is connected.
        
        Returns:
            True if connected, False otherwise
        """
        devices = self.devices()
        return self.device_id in devices if self.device_id else len(devices) > 0
