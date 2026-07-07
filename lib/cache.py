"""
Cache Engine - Manages UI state caching to avoid unnecessary dumps.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Any
from config.settings import CACHE_DIR, CACHE_ENABLED, CACHE_MAX_AGE
from lib.logs import setup_logger
from lib.exceptions import CacheError

logger = setup_logger("CacheEngine")


class CacheEntry:
    """Represents a single cache entry."""
    
    def __init__(self, data: Any, checksum: str, timestamp: float):
        self.data = data
        self.checksum = checksum
        self.timestamp = timestamp
    
    def is_valid(self) -> bool:
        """Check if cache entry is still valid based on age."""
        return (time.time() - self.timestamp) < CACHE_MAX_AGE


class CacheEngine:
    """
    Cache Engine - Avoids repetitive processing by caching UI state.
    
    Works by:
    1. Dump XML
    2. Calculate SHA256 hash
    3. If hash changed -> Update cache
    4. If hash unchanged -> Use cached data
    """
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        """
        Initialize CacheEngine.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self._cache: dict[str, CacheEntry] = {}
        self._current_checksum: Optional[str] = None
        self._enabled = CACHE_ENABLED
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _calculate_checksum(self, xml_content: str) -> str:
        """
        Calculate SHA256 checksum of XML content.
        
        Args:
            xml_content: XML string content
            
        Returns:
            SHA256 hex digest
        """
        return hashlib.sha256(xml_content.encode('utf-8')).hexdigest()
    
    def has_changed(self, xml_content: str) -> bool:
        """
        Check if UI has changed since last cache.
        
        Args:
            xml_content: Current XML content
            
        Returns:
            True if UI changed, False otherwise
        """
        if not self._enabled:
            return True
        
        new_checksum = self._calculate_checksum(xml_content)
        
        if self._current_checksum is None:
            logger.debug("No previous checksum, UI considered changed")
            return True
        
        has_changed = new_checksum != self._current_checksum
        
        if has_changed:
            logger.debug("UI changed detected")
        else:
            logger.debug("UI unchanged, using cache")
        
        return has_changed
    
    def update(self, xml_content: str, parsed_data: Any = None) -> str:
        """
        Update cache with new XML content.
        
        Args:
            xml_content: New XML content
            parsed_data: Optional parsed representation
            
        Returns:
            Checksum of the new content
        """
        checksum = self._calculate_checksum(xml_content)
        
        self._current_checksum = checksum
        self._cache['xml'] = CacheEntry(
            data=xml_content,
            checksum=checksum,
            timestamp=time.time()
        )
        
        if parsed_data is not None:
            self._cache['parsed'] = CacheEntry(
                data=parsed_data,
                checksum=checksum,
                timestamp=time.time()
            )
        
        logger.debug(f"Cache updated with checksum: {checksum[:16]}...")
        return checksum
    
    def get_xml(self) -> Optional[str]:
        """
        Get cached XML content.
        
        Returns:
            Cached XML string or None
        """
        if not self._enabled:
            return None
        
        if 'xml' in self._cache and self._cache['xml'].is_valid():
            logger.debug("Returning cached XML")
            return self._cache['xml'].data
        
        return None
    
    def get_parsed(self) -> Any:
        """
        Get cached parsed data.
        
        Returns:
            Cached parsed data or None
        """
        if not self._enabled:
            return None
        
        if 'parsed' in self._cache and self._cache['parsed'].is_valid():
            logger.debug("Returning cached parsed data")
            return self._cache['parsed'].data
        
        return None
    
    def invalidate(self) -> None:
        """Invalidate current cache."""
        self._current_checksum = None
        self._cache.clear()
        logger.debug("Cache invalidated")
    
    def clear(self) -> None:
        """Clear all cache including files."""
        self.invalidate()
        
        # Clear cache files
        for cache_file in self.cache_dir.glob("*"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")
        
        logger.info("Cache cleared")
    
    def save_to_file(self, name: str, data: Any) -> Path:
        """
        Save data to a cache file.
        
        Args:
            name: File name (without extension)
            data: Data to save (will be JSON serialized)
            
        Returns:
            Path to saved file
        """
        try:
            file_path = self.cache_dir / f"{name}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Saved cache file: {file_path}")
            return file_path
        except Exception as e:
            raise CacheError(f"Failed to save cache file: {e}")
    
    def load_from_file(self, name: str) -> Optional[Any]:
        """
        Load data from a cache file.
        
        Args:
            name: File name (without extension)
            
        Returns:
            Loaded data or None if not found
        """
        try:
            file_path = self.cache_dir / f"{name}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Loaded cache file: {file_path}")
            return data
        except Exception as e:
            logger.warning(f"Failed to load cache file: {e}")
            return None
    
    @property
    def checksum(self) -> Optional[str]:
        """Get current checksum."""
        return self._current_checksum
    
    @property
    def is_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable caching."""
        self._enabled = True
        logger.info("Cache enabled")
    
    def disable(self) -> None:
        """Disable caching."""
        self._enabled = False
        logger.info("Cache disabled")
