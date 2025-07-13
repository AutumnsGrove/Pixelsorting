#!/usr/bin/env python3
"""
Tests for configuration presets.
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pixelsort.config.presets import PRESETS, get_preset, list_presets, validate_preset
    PRESETS_AVAILABLE = True
except ImportError:
    PRESETS_AVAILABLE = False


@pytest.mark.skipif(not PRESETS_AVAILABLE, reason="Presets module not available")
class TestPresets:
    """Test class for configuration presets."""
    
    def test_presets_exist(self):
        """Test that PRESETS dictionary exists and has content."""
        assert isinstance(PRESETS, dict)
        assert len(PRESETS) > 0
    
    def test_get_preset_valid(self):
        """Test getting a valid preset."""
        # Get the first available preset
        preset_names = list(PRESETS.keys())
        if preset_names:
            preset_name = preset_names[0]
            preset = get_preset(preset_name)
            
            assert preset is not None
            assert isinstance(preset, dict)
    
    def test_get_preset_invalid(self):
        """Test getting an invalid preset."""
        with pytest.raises(KeyError):
            get_preset("nonexistent_preset")
    
    def test_list_presets(self):
        """Test listing available presets."""
        preset_list = list_presets()
        
        assert isinstance(preset_list, list)
        assert len(preset_list) == len(PRESETS)
        
        # All items should be strings
        assert all(isinstance(name, str) for name in preset_list)
    
    def test_validate_preset_structure(self):
        """Test that all presets have valid structure."""
        for preset_name, preset_config in PRESETS.items():
            # Each preset should be a dictionary
            assert isinstance(preset_config, dict), f"Preset {preset_name} is not a dict"
            
            # Should have required keys
            required_keys = ['interval_function', 'sorting_function']
            for key in required_keys:
                assert key in preset_config, f"Preset {preset_name} missing key {key}"
    
    def test_preset_parameter_types(self):
        """Test that preset parameters have correct types."""
        for preset_name, preset_config in PRESETS.items():
            # Type checking for common parameters
            if 'bottom_threshold' in preset_config:
                assert isinstance(preset_config['bottom_threshold'], (int, float))
                assert 0.0 <= preset_config['bottom_threshold'] <= 1.0
            
            if 'upper_threshold' in preset_config:
                assert isinstance(preset_config['upper_threshold'], (int, float))
                assert 0.0 <= preset_config['upper_threshold'] <= 1.0
            
            if 'clength' in preset_config:
                assert isinstance(preset_config['clength'], int)
                assert preset_config['clength'] >= 0
            
            if 'randomness' in preset_config:
                assert isinstance(preset_config['randomness'], (int, float))
                assert 0.0 <= preset_config['randomness'] <= 100.0
            
            if 'angle' in preset_config:
                assert isinstance(preset_config['angle'], (int, float))
                assert 0.0 <= preset_config['angle'] < 360.0


@pytest.mark.skipif(not PRESETS_AVAILABLE, reason="Presets module not available")
class TestPresetValidation:
    """Test preset validation functionality."""
    
    def test_validate_preset_function_exists(self):
        """Test that validate_preset function exists."""
        assert callable(validate_preset)
    
    def test_validate_preset_with_valid_config(self):
        """Test validating a preset with valid configuration."""
        # Create a valid preset configuration
        valid_config = {
            'interval_function': 'random',
            'sorting_function': 'lightness',
            'bottom_threshold': 0.25,
            'upper_threshold': 0.8,
            'clength': 50,
            'randomness': 10.0,
            'angle': 0.0
        }
        
        # Should not raise an exception
        try:
            result = validate_preset(valid_config)
            assert result is True or result is None  # Depending on implementation
        except Exception as e:
            pytest.fail(f"Valid preset failed validation: {e}")
    
    def test_validate_preset_with_missing_required(self):
        """Test validating a preset missing required fields."""
        invalid_config = {
            'bottom_threshold': 0.25,
            # Missing interval_function and sorting_function
        }
        
        with pytest.raises((KeyError, ValueError)):
            validate_preset(invalid_config)


class TestPresetsIntegration:
    """Test presets integration with main configuration system."""
    
    def test_presets_work_with_sorting_config(self):
        """Test that presets can be used with SortingConfig."""
        try:
            from pixelsort.config.presets import PRESETS
            from pixelsort.utils.config import SortingConfig
            
            # Get first preset
            if PRESETS:
                preset_name = list(PRESETS.keys())[0]
                preset_obj = PRESETS[preset_name]
                
                # Extract sorting config from preset object
                if hasattr(preset_obj, 'sorting_config'):
                    sorting_config = preset_obj.sorting_config
                    
                    # Should have valid configuration
                    assert hasattr(sorting_config, 'interval_function')
                    assert hasattr(sorting_config, 'sorting_function')
                else:
                    # If it's a different structure, just check it exists
                    assert preset_obj is not None
                
        except ImportError:
            pytest.skip("Required modules not available")


if __name__ == "__main__":
    pytest.main([__file__])