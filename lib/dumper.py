"""
XML Dumper - Obtains and manages UI XML dumps from Android device.
"""

import time
from pathlib import Path
from typing import Optional
from lib.adb_bridge import ADBBridge
from lib.logs import setup_logger
from lib.exceptions import ADBCommandError
from config.settings import DUMP_TIMEOUT, DUMP_RETRY_COUNT, DUMPS_DIR

logger = setup_logger("XMLDumper")


class XMLDumper:
    """
    XML Dumper - Responsible for obtaining UI XML dumps from Android device.
    
    Provides methods to:
    - dump(): Get current UI XML
    - save(): Save XML to file
    - load(): Load XML from file
    - refresh(): Force refresh of cached dump
    - parse(): Parse XML into UIElement tree
    """
    
    def __init__(self, adb: ADBBridge, dumps_dir: Path = DUMPS_DIR):
        """
        Initialize XMLDumper.
        
        Args:
            adb: ADBBridge instance for executing commands
            dumps_dir: Directory to save dump files
        """
        self.adb = adb
        self.dumps_dir = dumps_dir
        self._last_dump: Optional[str] = None
        self._last_dump_time: float = 0
        
        # Ensure dumps directory exists
        self.dumps_dir.mkdir(parents=True, exist_ok=True)
    
    def dump(self, timeout: int = DUMP_TIMEOUT, retry_count: int = DUMP_RETRY_COUNT) -> str:
        """
        Dump the current UI hierarchy as XML.
        
        Args:
            timeout: Timeout for each dump attempt in seconds
            retry_count: Number of retry attempts
            
        Returns:
            XML string content
            
        Raises:
            ADBCommandError: If all dump attempts fail
        """
        last_error = None
        
        for attempt in range(retry_count):
            try:
                logger.debug(f"Dumping UI (attempt {attempt + 1}/{retry_count})...")
                
                # Use uiautomator dump if available, fallback to dumpsys
                xml_content = self._dump_uiautomator(timeout)
                
                if not xml_content or len(xml_content) < 100:
                    # Fallback to dumpsys window
                    xml_content = self._dump_dumpsys(timeout)
                
                if xml_content and len(xml_content) > 100:
                    self._last_dump = xml_content
                    self._last_dump_time = time.time()
                    logger.info(f"Successfully dumped UI ({len(xml_content)} bytes)")
                    return xml_content
                
                last_error = "Empty or invalid dump received"
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Dump attempt {attempt + 1} failed: {e}")
            
            if attempt < retry_count - 1:
                time.sleep(0.5)  # Wait before retry
        
        raise ADBCommandError(f"Failed to dump UI after {retry_count} attempts: {last_error}")
    
    def _dump_uiautomator(self, timeout: int) -> Optional[str]:
        """
        Dump using uiautomator.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            XML content or None
        """
        try:
            # Try using uiautomator2's dump method via shell
            temp_file = "/sdcard/window_dump.xml"
            
            # Execute dump
            self.adb.shell(f"uiautomator dump {temp_file}")
            time.sleep(0.3)
            
            # Pull the file content
            output = self.adb.shell(f"cat {temp_file}")
            
            # Clean up
            self.adb.shell(f"rm {temp_file}")
            
            if output and "<?xml" in output:
                return output
            
            return None
            
        except Exception as e:
            logger.debug(f"uiautomator dump failed: {e}")
            return None
    
    def _dump_dumpsys(self, timeout: int) -> Optional[str]:
        """
        Dump using dumpsys (fallback method).
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            XML-like content or None
        """
        try:
            output = self.adb.dumpsys("window")
            if output:
                # Note: This is not true XML but can be useful
                return f"<dump source=\"dumpsys\">{output}</dump>"
            return None
        except Exception as e:
            logger.debug(f"dumpsys failed: {e}")
            return None
    
    def save(self, filename: Optional[str] = None) -> Path:
        """
        Save the last dump to a file.
        
        Args:
            filename: Optional filename. If None, generates timestamp-based name.
            
        Returns:
            Path to saved file
            
        Raises:
            ValueError: If no dump is available
        """
        if not self._last_dump:
            raise ValueError("No dump available. Call dump() first.")
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"ui_dump_{timestamp}.xml"
        
        file_path = self.dumps_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self._last_dump)
        
        logger.info(f"Saved dump to {file_path}")
        return file_path
    
    def load(self, file_path: Path) -> str:
        """
        Load XML from a file.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            XML content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Loaded dump from {file_path}")
        self._last_dump = content
        return content
    
    def refresh(self) -> str:
        """
        Force refresh and get a new dump.
        
        Returns:
            Fresh XML content
        """
        logger.debug("Forcing UI dump refresh...")
        self._last_dump = None
        return self.dump()
    
    def parse(self, xml_content: Optional[str] = None):
        """
        Parse XML content into UIElement tree.
        
        Args:
            xml_content: Optional XML content. If None, uses last dump.
            
        Returns:
            Parsed UIElement tree
        """
        from lib.parser import XMLParser
        
        if xml_content is None:
            if not self._last_dump:
                xml_content = self.dump()
            else:
                xml_content = self._last_dump
        
        parser = XMLParser()
        return parser.parse(xml_content)
    
    @property
    def last_dump(self) -> Optional[str]:
        """Get the last dumped XML content."""
        return self._last_dump
    
    @property
    def last_dump_time(self) -> float:
        """Get the timestamp of the last dump."""
        return self._last_dump_time
    
    def is_fresh(self, max_age: float = 2.0) -> bool:
        """
        Check if the last dump is fresh enough.
        
        Args:
            max_age: Maximum age in seconds to consider fresh
            
        Returns:
            True if dump is fresh, False otherwise
        """
        if not self._last_dump:
            return False
        return (time.time() - self._last_dump_time) < max_age
