#!/usr/bin/env python3
"""
Tests for sorting functions.
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.effects.sorting_functions import (
    lightness_sort, intensity_sort, hue_sort, saturation_sort,
    minimum_sort, maximum_sort, red_sort, green_sort, blue_sort, alpha_sort,
    get_sorting_function, list_sorting_functions, SORTING_FUNCTIONS
)


class TestSortingFunctions:
    """Test class for sorting functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_pixel_red = (255, 0, 0, 255)  # Pure red
        self.test_pixel_green = (0, 255, 0, 255)  # Pure green
        self.test_pixel_blue = (0, 0, 255, 255)  # Pure blue
        self.test_pixel_white = (255, 255, 255, 255)  # White
        self.test_pixel_black = (0, 0, 0, 255)  # Black
        self.test_pixel_gray = (128, 128, 128, 255)  # Gray
        self.test_pixel_transparent = (255, 255, 255, 0)  # Transparent
    
    def test_lightness_sort(self):
        """Test lightness sorting function."""
        # Test that white has higher lightness than black
        white_lightness = lightness_sort(self.test_pixel_white)
        black_lightness = lightness_sort(self.test_pixel_black)
        assert white_lightness > black_lightness
        
        # Test that lightness values are in valid range [0, 1]
        assert 0.0 <= white_lightness <= 1.0
        assert 0.0 <= black_lightness <= 1.0
    
    def test_intensity_sort(self):
        """Test intensity sorting function."""
        # Test that white has higher intensity than black
        white_intensity = intensity_sort(self.test_pixel_white)
        black_intensity = intensity_sort(self.test_pixel_black)
        assert white_intensity > black_intensity
        
        # Test specific values
        assert white_intensity == 765  # 255 + 255 + 255
        assert black_intensity == 0    # 0 + 0 + 0
    
    def test_hue_sort(self):
        """Test hue sorting function."""
        # Test that different colors have different hues
        red_hue = hue_sort(self.test_pixel_red)
        green_hue = hue_sort(self.test_pixel_green)
        blue_hue = hue_sort(self.test_pixel_blue)
        
        # Test that hue values are in valid range [0, 1]
        assert 0.0 <= red_hue <= 1.0
        assert 0.0 <= green_hue <= 1.0
        assert 0.0 <= blue_hue <= 1.0
        
        # Test that pure colors have distinct hues
        hues = [red_hue, green_hue, blue_hue]
        assert len(set(hues)) == 3  # All different
    
    def test_saturation_sort(self):
        """Test saturation sorting function."""
        # Test that pure colors have higher saturation than gray
        red_saturation = saturation_sort(self.test_pixel_red)
        gray_saturation = saturation_sort(self.test_pixel_gray)
        
        assert red_saturation > gray_saturation
        assert 0.0 <= red_saturation <= 1.0
        assert 0.0 <= gray_saturation <= 1.0
    
    def test_minimum_sort(self):
        """Test minimum RGB value sorting."""
        # Test specific values
        red_min = minimum_sort(self.test_pixel_red)
        white_min = minimum_sort(self.test_pixel_white)
        
        assert red_min == 0    # min(255, 0, 0)
        assert white_min == 255  # min(255, 255, 255)
    
    def test_maximum_sort(self):
        """Test maximum RGB value sorting."""
        # Test specific values
        red_max = maximum_sort(self.test_pixel_red)
        black_max = maximum_sort(self.test_pixel_black)
        
        assert red_max == 255  # max(255, 0, 0)
        assert black_max == 0  # max(0, 0, 0)
    
    def test_color_channel_sorts(self):
        """Test individual color channel sorting functions."""
        # Test red channel
        assert red_sort(self.test_pixel_red) == 255
        assert red_sort(self.test_pixel_green) == 0
        
        # Test green channel
        assert green_sort(self.test_pixel_green) == 255
        assert green_sort(self.test_pixel_red) == 0
        
        # Test blue channel
        assert blue_sort(self.test_pixel_blue) == 255
        assert blue_sort(self.test_pixel_red) == 0
    
    def test_alpha_sort(self):
        """Test alpha channel sorting."""
        assert alpha_sort(self.test_pixel_white) == 255
        assert alpha_sort(self.test_pixel_transparent) == 0
    
    def test_get_sorting_function(self):
        """Test getting sorting functions by name."""
        # Test valid function names
        func = get_sorting_function("lightness")
        assert func == lightness_sort
        
        func = get_sorting_function("intensity")
        assert func == intensity_sort
        
        # Test invalid function name
        with pytest.raises((KeyError, Exception)):  # Custom exception or KeyError
            get_sorting_function("invalid_function")
    
    def test_list_sorting_functions(self):
        """Test listing available sorting functions."""
        functions = list_sorting_functions()
        assert isinstance(functions, list)
        assert len(functions) > 0
        assert "lightness" in functions
        assert "intensity" in functions
        assert "hue" in functions
    
    def test_sorting_functions_registry(self):
        """Test the sorting functions registry."""
        assert isinstance(SORTING_FUNCTIONS, dict)
        assert len(SORTING_FUNCTIONS) > 0
        
        # Test that all listed functions are in registry
        for name in list_sorting_functions():
            assert name in SORTING_FUNCTIONS
            assert callable(SORTING_FUNCTIONS[name])


if __name__ == "__main__":
    pytest.main([__file__])
