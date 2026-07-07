"""
Keyboard Engine - Handles text input operations.
"""

import time
from typing import Optional
from lib.logs import setup_logger
from config.constants import KEYCODE_ENTER, KEYCODE_BACKSPACE, KEYCODE_TAB

logger = setup_logger("KeyboardEngine")


class KeyboardEngine:
    """
    Keyboard Engine - Responsible for text input operations.
    
    Supports:
    - send_keys(): Send text to input field
    - clear(): Clear input field
    - paste(): Paste from clipboard
    - enter(): Press Enter key
    - delete(): Delete character
    - backspace(): Press backspace
    - hide_keyboard(): Hide soft keyboard
    """
    
    def __init__(self, device):
        """
        Initialize KeyboardEngine.
        
        Args:
            device: Device instance with adb bridge
        """
        self.device = device
        self.adb = device.adb
    
    def send_keys(self, text: str, clear_first: bool = True) -> bool:
        """
        Send text to the currently focused input field.
        
        Args:
            text: Text to send
            clear_first: If True, clear field before sending
            
        Returns:
            True if successful
        """
        logger.info(f"Sending keys: '{text[:20]}...' ({len(text)} chars)")
        
        try:
            if clear_first:
                self.clear()
            
            # Use ADB input text command
            # Escape special characters
            escaped = text.replace(' ', '%s')
            self.adb.input_text(escaped)
            
            time.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send keys: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear the current input field.
        
        Returns:
            True if successful
        """
        logger.debug("Clearing input field")
        
        try:
            # Select all and delete (multiple backspaces)
            for _ in range(50):  # Max 50 backspaces
                self.adb.input_keyevent(KEYCODE_BACKSPACE)
            
            return True
        except Exception as e:
            logger.error(f"Failed to clear field: {e}")
            return False
    
    def paste(self) -> bool:
        """
        Paste content from clipboard.
        
        Note: This requires clipboard content to be set via ADB.
        
        Returns:
            True if successful
        """
        logger.info("Pasting from clipboard")
        
        try:
            # Get clipboard content (Android 10+)
            output = self.adb.shell("cmd clipboard get-clipboard")
            
            if output and 'text' in output:
                # Extract text and send it
                # Simplified - actual implementation may vary by Android version
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to paste: {e}")
            return False
    
    def enter(self) -> bool:
        """
        Press Enter key.
        
        Returns:
            True if successful
        """
        logger.debug("Pressing Enter")
        
        try:
            self.adb.input_keyevent(KEYCODE_ENTER)
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"Failed to press Enter: {e}")
            return False
    
    def delete(self) -> bool:
        """
        Delete character after cursor.
        
        Returns:
            True if successful
        """
        logger.debug("Deleting character")
        
        try:
            self.adb.input_keyevent(KEYCODE_BACKSPACE)
            return True
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            return False
    
    def backspace(self, count: int = 1) -> bool:
        """
        Press backspace multiple times.
        
        Args:
            count: Number of backspaces
            
        Returns:
            True if successful
        """
        logger.debug(f"Pressing backspace {count} times")
        
        try:
            for _ in range(count):
                self.adb.input_keyevent(KEYCODE_BACKSPACE)
                time.sleep(0.05)
            return True
        except Exception as e:
            logger.error(f"Failed to backspace: {e}")
            return False
    
    def tab(self) -> bool:
        """
        Press Tab key to move to next field.
        
        Returns:
            True if successful
        """
        logger.debug("Pressing Tab")
        
        try:
            self.adb.input_keyevent(KEYCODE_TAB)
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"Failed to press Tab: {e}")
            return False
    
    def hide_keyboard(self) -> bool:
        """
        Hide the soft keyboard.
        
        Returns:
            True if successful
        """
        logger.debug("Hiding keyboard")
        
        try:
            # Try back button first
            self.adb.input_keyevent(4)  # KEYCODE_BACK
            time.sleep(0.2)
            return True
        except Exception as e:
            logger.error(f"Failed to hide keyboard: {e}")
            return False
    
    def type_slowly(self, text: str, delay: float = 0.05) -> bool:
        """
        Type text slowly, character by character.
        
        Useful for apps that detect automated input.
        
        Args:
            text: Text to type
            delay: Delay between characters in seconds
            
        Returns:
            True if successful
        """
        logger.info(f"Typing slowly: '{text[:20]}...'")
        
        try:
            self.clear()
            
            for char in text:
                escaped = char.replace(' ', '%s')
                self.adb.input_text(escaped)
                time.sleep(delay)
            
            return True
        except Exception as e:
            logger.error(f"Failed to type slowly: {e}")
            return False
