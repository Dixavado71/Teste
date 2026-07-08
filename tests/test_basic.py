"""
Basic unit tests for dixUIAuto framework.

Run with: pytest tests/test_basic.py -v
Or: python -m pytest tests/ -v --cov=lib
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestModels:
    """Tests for data models."""
    
    def test_bounds_creation(self):
        """Test Bounds dataclass creation and properties."""
        from lib.models import Bounds
        
        bounds = Bounds(left=0, top=0, right=100, bottom=200)
        
        assert bounds.width == 100
        assert bounds.height == 200
        assert bounds.center_x == 50
        assert bounds.center_y == 100
        assert bounds.center == (50, 100)
    
    def test_bounds_contains_point(self):
        """Test point containment check."""
        from lib.models import Bounds
        
        bounds = Bounds(left=0, top=0, right=100, bottom=100)
        
        assert bounds.contains_point(50, 50) is True
        assert bounds.contains_point(0, 0) is True
        assert bounds.contains_point(100, 100) is True
        assert bounds.contains_point(101, 101) is False
        assert bounds.contains_point(-1, -1) is False
    
    def test_bounds_from_string(self):
        """Test parsing bounds from string."""
        from lib.models import Bounds
        
        bounds = Bounds.from_string("[0,100][200,300]")
        
        assert bounds.left == 0
        assert bounds.top == 100
        assert bounds.right == 200
        assert bounds.bottom == 300
    
    def test_ui_element_creation(self):
        """Test UIElement dataclass creation."""
        from lib.models import UIElement, Bounds
        
        element = UIElement(
            text="Login",
            resource_id="com.app:id/login_btn",
            clazz="android.widget.Button",
            clickable=True,
            enabled=True
        )
        
        assert element.text == "Login"
        assert element.id == "com.app:id/login_btn"
        assert element.is_interactable is True
    
    def test_ui_element_with_bounds(self):
        """Test UIElement with bounds properties."""
        from lib.models import UIElement, Bounds
        
        bounds = Bounds(left=0, top=0, right=100, bottom=50)
        element = UIElement(text="Test", bounds=bounds, enabled=True)
        
        assert element.is_visible is True
        assert element.get_text() == "Test"


class TestCache:
    """Tests for cache engine."""
    
    def test_cache_initialization(self):
        """Test CacheEngine initialization."""
        from lib.cache import CacheEngine
        
        cache = CacheEngine()
        
        assert cache.checksum is None
        assert cache.has_changed("new content") is True
    
    def test_cache_update(self):
        """Test cache update functionality."""
        from lib.cache import CacheEngine
        
        cache = CacheEngine()
        content = "<xml>test</xml>"
        
        cache.update(content)
        
        assert cache.checksum is not None
        assert cache.has_changed(content) is False
        assert cache.has_changed("<xml>different</xml>") is True


class TestExceptions:
    """Tests for custom exceptions."""
    
    def test_dixuiauto_error(self):
        """Test DixUIAutoError exception."""
        from lib.exceptions import DixUIAutoError
        
        error = DixUIAutoError("Test error message")
        
        assert str(error) == "Test error message"
    
    def test_element_not_found_error(self):
        """Test ElementNotFoundError exception."""
        from lib.exceptions import ElementNotFoundError
        
        error = ElementNotFoundError("text", "Login")
        
        assert "text" in str(error)
        assert "Login" in str(error)


class TestLocator:
    """Tests for spatial locator."""
    
    def test_distance_calculation(self):
        """Test distance calculation between points."""
        from lib.locator import Locator
        
        locator = Locator()
        
        # Test same point
        dist = locator.calculate_distance((0, 0), (0, 0))
        assert dist == 0
        
        # Test horizontal distance
        dist = locator.calculate_distance((0, 0), (10, 0))
        assert dist == 10
        
        # Test vertical distance
        dist = locator.calculate_distance((0, 0), (0, 10))
        assert dist == 10
    
    def test_center_calculation(self):
        """Test center point calculation."""
        from lib.locator import Locator
        
        locator = Locator()
        center = locator.get_screen_center(1080, 1920)
        
        assert center == (540, 960)


class TestValidator:
    """Tests for validator module."""
    
    def test_validator_initialization(self):
        """Test Validator initialization."""
        from lib.validator import Validator
        
        mock_finder = Mock()
        validator = Validator(mock_finder)
        
        assert validator.finder == mock_finder


class TestSettings:
    """Tests for configuration settings."""
    
    def test_settings_defaults(self):
        """Test default settings values."""
        from config.settings import Settings
        
        settings = Settings()
        
        assert settings.ADB_HOST == "127.0.0.1"
        assert settings.ADB_PORT == 5037
        assert settings.CACHE_ENABLED is True
        assert settings.LOG_LEVEL == "INFO"
    
    def test_settings_to_dict(self):
        """Test settings to dictionary conversion."""
        from config.settings import Settings
        
        settings = Settings()
        settings_dict = settings.to_dict()
        
        assert isinstance(settings_dict, dict)
        assert 'ADB_HOST' in settings_dict
        assert 'LOG_LEVEL' in settings_dict


class TestConstants:
    """Tests for framework constants."""
    
    def test_attribute_constants(self):
        """Test attribute constant definitions."""
        from config.constants import (
            ATTR_TEXT, ATTR_RESOURCE_ID, ATTR_CLASS,
            ATTR_CONTENT_DESC, ATTR_BOUNDS
        )
        
        assert ATTR_TEXT == "text"
        assert ATTR_RESOURCE_ID == "resource-id"
        assert ATTR_CLASS == "class"
        assert ATTR_CONTENT_DESC == "content-desc"
        assert ATTR_BOUNDS == "bounds"
    
    def test_direction_constants(self):
        """Test direction constant definitions."""
        from config.constants import (
            DIRECTION_UP, DIRECTION_DOWN,
            DIRECTION_LEFT, DIRECTION_RIGHT
        )
        
        assert DIRECTION_UP == "up"
        assert DIRECTION_DOWN == "down"
        assert DIRECTION_LEFT == "left"
        assert DIRECTION_RIGHT == "right"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
