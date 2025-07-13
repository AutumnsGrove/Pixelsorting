#!/usr/bin/env python3
"""
Tests for core sorting functionality.
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.core.sorting import sort_image, sort_interval
from pixelsort.effects.sorting_functions import lightness_sort, intensity_sort


class TestCoreSorting:
    """Test class for core sorting functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create test pixel arrays
        self.test_pixels = [
            [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)],  # Red, Green, Blue
            [(128, 128, 128, 255), (255, 255, 255, 255), (0, 0, 0, 255)]  # Gray, White, Black
        ]
        
        # Create test intervals
        self.test_intervals = [
            [3],  # Sort entire first row
            [3]   # Sort entire second row
        ]
        
        # Test arguments
        self.test_args = {
            "randomness": 0.0,  # No randomness for predictable tests
        }
    
    def test_sort_interval_lightness(self):
        """Test sorting pixels in a single interval by lightness."""
        # Row with different lightness pixels: Black, Gray, White
        row = [(0, 0, 0, 255), (128, 128, 128, 255), (255, 255, 255, 255)]
        
        # Shuffle them to ensure sorting is needed
        test_row = [row[2], row[0], row[1]]  # White, Black, Gray
        
        # Sort by lightness
        sorted_row = sort_interval(test_row, lightness_sort)
        
        # Check that sorting happened
        assert len(sorted_row) == 3
        assert sorted_row != test_row  # Should be different order
        
        # Verify lightness ordering (darkest to lightest)
        lightness_values = [lightness_sort(pixel) for pixel in sorted_row]
        assert lightness_values == sorted(lightness_values)
    
    def test_sort_interval_intensity(self):
        """Test sorting pixels in a single interval by intensity."""
        # Row with different intensity pixels
        row = [(255, 0, 0, 255), (128, 128, 128, 255), (255, 255, 255, 255)]
        
        # Sort by intensity
        sorted_row = sort_interval(row, intensity_sort)
        
        # Check that sorting happened
        assert len(sorted_row) == 3
        
        # Verify intensity ordering
        intensity_values = [intensity_sort(pixel) for pixel in sorted_row]
        assert intensity_values == sorted(intensity_values)
    
    def test_sort_image_complete(self):
        """Test sorting a complete image."""
        # Sort the test image
        sorted_pixels = sort_image(self.test_pixels, self.test_intervals, self.test_args, lightness_sort)
        
        # Check structure is preserved
        assert len(sorted_pixels) == len(self.test_pixels)
        assert len(sorted_pixels[0]) == len(self.test_pixels[0])
        assert len(sorted_pixels[1]) == len(self.test_pixels[1])
        
        # Check that pixels are still valid RGBA tuples
        for row in sorted_pixels:
            for pixel in row:
                assert len(pixel) == 4
                assert all(0 <= channel <= 255 for channel in pixel)
    
    def test_sort_image_with_randomness(self):
        """Test sorting with randomness parameter."""
        # Set high randomness (some intervals won't be sorted)
        random_args = {"randomness": 50.0}
        
        sorted_pixels = sort_image(self.test_pixels, self.test_intervals, random_args, lightness_sort)
        
        # Should still have correct structure
        assert len(sorted_pixels) == len(self.test_pixels)
        assert len(sorted_pixels[0]) == len(self.test_pixels[0])
    
    def test_sort_image_empty_intervals(self):
        """Test sorting with empty intervals."""
        empty_intervals = [[], []]
        
        sorted_pixels = sort_image(self.test_pixels, empty_intervals, self.test_args, lightness_sort)
        
        # Should return empty rows when no intervals
        assert len(sorted_pixels) == len(self.test_pixels)
        # With empty intervals, the function adds the first pixel of each row
        for i, row in enumerate(sorted_pixels):
            if len(self.test_pixels[i]) > 0:
                assert len(row) >= 1
    
    def test_sort_image_partial_intervals(self):
        """Test sorting with partial intervals."""
        # Only sort first pixel of each row
        partial_intervals = [
            [1, 3],  # Sort first pixel, then rest unsorted
            [1, 3]   # Same for second row
        ]
        
        sorted_pixels = sort_image(self.test_pixels, partial_intervals, self.test_args, lightness_sort)
        
        # Should have correct structure
        assert len(sorted_pixels) == len(self.test_pixels)
        assert len(sorted_pixels[0]) == len(self.test_pixels[0])


class TestSortingEdgeCases:
    """Test edge cases in sorting functionality."""
    
    def test_single_pixel_interval(self):
        """Test sorting interval with single pixel."""
        single_pixel = [(255, 0, 0, 255)]
        
        sorted_pixel = sort_interval(single_pixel, lightness_sort)
        
        # Single pixel should remain unchanged
        assert sorted_pixel == single_pixel
    
    def test_identical_pixels(self):
        """Test sorting interval with identical pixels."""
        identical_pixels = [(128, 128, 128, 255)] * 5
        
        sorted_pixels = sort_interval(identical_pixels, lightness_sort)
        
        # Identical pixels should remain in same order
        assert sorted_pixels == identical_pixels
    
    def test_large_interval(self):
        """Test sorting larger interval."""
        # Create gradient of gray pixels
        large_interval = []
        for i in range(20):
            gray_value = i * 12  # 0 to 228 in steps
            if gray_value > 255:
                gray_value = 255
            large_interval.append((gray_value, gray_value, gray_value, 255))
        
        # Reverse the order to test sorting
        large_interval.reverse()
        
        sorted_pixels = sort_interval(large_interval, lightness_sort)
        
        # Should be sorted by lightness
        lightness_values = [lightness_sort(pixel) for pixel in sorted_pixels]
        assert lightness_values == sorted(lightness_values)
        assert len(sorted_pixels) == 20


if __name__ == "__main__":
    pytest.main([__file__])