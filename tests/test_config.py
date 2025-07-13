#!/usr/bin/env python3
"""
Tests for configuration utilities.
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.utils.config import SortingConfig, validate_config


class TestSortingConfig:
    """Test class for SortingConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SortingConfig()
        
        assert config.bottom_threshold == 0.25
        assert config.upper_threshold == 0.8
        assert config.clength == 50
        assert config.randomness == 10.0
        assert config.angle == 0.0
        assert config.interval_function == "random"
        assert config.sorting_function == "lightness"
        assert config.url == ""
        assert config.internet is True
    
    def test_custom_config(self):
        """Test configuration with custom values."""
        config = SortingConfig(
            bottom_threshold=0.1,
            upper_threshold=0.9,
            clength=100,
            randomness=20.0,
            angle=45.0,
            interval_function="threshold",
            sorting_function="intensity"
        )
        
        assert config.bottom_threshold == 0.1
        assert config.upper_threshold == 0.9
        assert config.clength == 100
        assert config.randomness == 20.0
        assert config.angle == 45.0
        assert config.interval_function == "threshold"
        assert config.sorting_function == "intensity"
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = SortingConfig(bottom_threshold=0.1, clength=100)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["bottom_threshold"] == 0.1
        assert config_dict["clength"] == 100
        assert "int_function" in config_dict  # Note: different key name
        assert config_dict["int_function"] == "random"
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "bottom_threshold": 0.15,
            "upper_threshold": 0.85,
            "clength": 75,
            "randomness": 15.0,
            "angle": 30.0,
            "interval_function": "edges",
            "sorting_function": "hue"
        }
        
        config = SortingConfig.from_dict(config_dict)
        
        assert config.bottom_threshold == 0.15
        assert config.upper_threshold == 0.85
        assert config.clength == 75
        assert config.randomness == 15.0
        assert config.angle == 30.0
        assert config.interval_function == "edges"
        assert config.sorting_function == "hue"
    
    def test_from_dict_partial(self):
        """Test creating config from partial dictionary."""
        config_dict = {
            "bottom_threshold": 0.2,
            "clength": 200
        }
        
        config = SortingConfig.from_dict(config_dict)
        
        # Check overridden values
        assert config.bottom_threshold == 0.2
        assert config.clength == 200
        
        # Check default values are preserved
        assert config.upper_threshold == 0.8
        assert config.randomness == 10.0


class TestConfigValidation:
    """Test class for configuration validation."""
    
    def test_valid_config(self):
        """Test validation of valid configuration."""
        config = SortingConfig(
            bottom_threshold=0.3,
            upper_threshold=0.7,
            clength=50,
            randomness=15.0,
            angle=45.0
        )
        
        assert validate_config(config) is True
    
    def test_invalid_bottom_threshold_low(self):
        """Test validation with bottom threshold too low."""
        config = SortingConfig(bottom_threshold=-0.1)
        
        with pytest.raises(ValueError, match="bottom_threshold must be between 0.0 and 1.0"):
            validate_config(config)
    
    def test_invalid_bottom_threshold_high(self):
        """Test validation with bottom threshold too high."""
        config = SortingConfig(bottom_threshold=1.1)
        
        with pytest.raises(ValueError, match="bottom_threshold must be between 0.0 and 1.0"):
            validate_config(config)
    
    def test_invalid_upper_threshold_low(self):
        """Test validation with upper threshold too low."""
        config = SortingConfig(upper_threshold=-0.1)
        
        with pytest.raises(ValueError, match="upper_threshold must be between 0.0 and 1.0"):
            validate_config(config)
    
    def test_invalid_upper_threshold_high(self):
        """Test validation with upper threshold too high."""
        config = SortingConfig(upper_threshold=1.1)
        
        with pytest.raises(ValueError, match="upper_threshold must be between 0.0 and 1.0"):
            validate_config(config)
    
    def test_invalid_threshold_order(self):
        """Test validation with bottom >= upper threshold."""
        config = SortingConfig(bottom_threshold=0.8, upper_threshold=0.3)
        
        with pytest.raises(ValueError, match="bottom_threshold must be less than upper_threshold"):
            validate_config(config)
    
    def test_invalid_threshold_equal(self):
        """Test validation with equal thresholds."""
        config = SortingConfig(bottom_threshold=0.5, upper_threshold=0.5)
        
        with pytest.raises(ValueError, match="bottom_threshold must be less than upper_threshold"):
            validate_config(config)
    
    def test_invalid_clength_negative(self):
        """Test validation with negative clength."""
        config = SortingConfig(clength=-10)
        
        with pytest.raises(ValueError, match="clength must be non-negative"):
            validate_config(config)
    
    def test_invalid_randomness_low(self):
        """Test validation with randomness too low."""
        config = SortingConfig(randomness=-5.0)
        
        with pytest.raises(ValueError, match="randomness must be between 0.0 and 100.0"):
            validate_config(config)
    
    def test_invalid_randomness_high(self):
        """Test validation with randomness too high."""
        config = SortingConfig(randomness=150.0)
        
        with pytest.raises(ValueError, match="randomness must be between 0.0 and 100.0"):
            validate_config(config)
    
    def test_invalid_angle_negative(self):
        """Test validation with negative angle."""
        config = SortingConfig(angle=-10.0)
        
        with pytest.raises(ValueError, match="angle must be between 0.0 and 360.0"):
            validate_config(config)
    
    def test_invalid_angle_high(self):
        """Test validation with angle >= 360."""
        config = SortingConfig(angle=370.0)
        
        with pytest.raises(ValueError, match="angle must be between 0.0 and 360.0"):
            validate_config(config)
    
    def test_boundary_values(self):
        """Test validation with boundary values."""
        # Test valid boundary values
        config = SortingConfig(
            bottom_threshold=0.0,
            upper_threshold=1.0,
            clength=0,
            randomness=0.0,
            angle=0.0
        )
        assert validate_config(config) is True
        
        config = SortingConfig(
            bottom_threshold=0.0,
            upper_threshold=1.0,
            clength=1000,
            randomness=100.0,
            angle=359.9
        )
        assert validate_config(config) is True


if __name__ == "__main__":
    pytest.main([__file__])
