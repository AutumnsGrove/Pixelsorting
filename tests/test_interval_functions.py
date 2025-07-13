#!/usr/bin/env python3
"""
Tests for interval functions.
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.effects.interval_functions import (
    random_intervals, threshold_intervals, wave_intervals, no_intervals,
    get_interval_function, list_interval_functions, INTERVAL_FUNCTIONS,
    random_width, append_black_white_pixel, BLACK_PIXEL, WHITE_PIXEL
)


class TestIntervalFunctions:
    """Test class for interval functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create test pixel array (3x3 red pixels)
        self.test_pixels = [
            [(255, 0, 0, 255), (255, 0, 0, 255), (255, 0, 0, 255)],
            [(255, 0, 0, 255), (255, 0, 0, 255), (255, 0, 0, 255)],
            [(255, 0, 0, 255), (255, 0, 0, 255), (255, 0, 0, 255)]
        ]
        
        # Create test arguments
        self.test_args = {
            "clength": 2,
            "bottom_threshold": 0.2,
            "upper_threshold": 0.8,
            "url": "",
            "internet": False,
            "angle": 0
        }
        
        # Create temporary test image
        self.temp_image = Image.new("RGBA", (3, 3), (255, 0, 0, 255))
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.temp_image.save(self.temp_file.name)
        self.temp_file.close()
        self.test_args["url"] = self.temp_file.name
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_random_width(self):
        """Test random width generation."""
        width = random_width(10.0)
        assert 0.0 <= width <= 10.0
        
        # Test multiple calls produce different values (with high probability)
        widths = [random_width(10.0) for _ in range(10)]
        assert len(set(widths)) > 1  # Should get some variation
    
    def test_append_black_white_pixel(self):
        """Test black/white pixel appending."""
        pixel_list = [[], [], []]
        
        # Test with a dark pixel (should append white)
        dark_pixels = [[(50, 50, 50, 255)] * 3] * 3
        append_black_white_pixel(pixel_list, 0, 0, dark_pixels, 0.5)
        assert pixel_list[0][0] == WHITE_PIXEL
        
        # Test with a bright pixel (should append black)
        bright_pixels = [[(200, 200, 200, 255)] * 3] * 3
        append_black_white_pixel(pixel_list, 0, 1, bright_pixels, 0.5)
        assert pixel_list[1][0] == BLACK_PIXEL
    
    def test_random_intervals(self):
        """Test random interval generation."""
        intervals = random_intervals(self.test_pixels, self.test_args)
        
        # Check structure
        assert len(intervals) == len(self.test_pixels)  # One row per pixel row
        
        # Check each row has intervals
        for row_intervals in intervals:
            assert isinstance(row_intervals, list)
            assert len(row_intervals) > 0
            # Last interval should be image width
            assert row_intervals[-1] == len(self.test_pixels[0])
    
    def test_threshold_intervals(self):
        """Test threshold-based interval generation."""
        intervals = threshold_intervals(self.test_pixels, self.test_args)
        
        # Check structure
        assert len(intervals) == len(self.test_pixels)
        
        # Check each row has intervals
        for row_intervals in intervals:
            assert isinstance(row_intervals, list)
            # Should at least have the final interval
            assert row_intervals[-1] == len(self.test_pixels[0])
    
    def test_wave_intervals(self):
        """Test wave interval generation."""
        intervals = wave_intervals(self.test_pixels, self.test_args)
        
        # Check structure
        assert len(intervals) == len(self.test_pixels)
        
        # Check each row has intervals
        for row_intervals in intervals:
            assert isinstance(row_intervals, list)
            assert len(row_intervals) > 0
            assert row_intervals[-1] == len(self.test_pixels[0])
    
    def test_no_intervals(self):
        """Test no intervals (single interval per row)."""
        intervals = no_intervals(self.test_pixels, self.test_args)
        
        # Check structure
        assert len(intervals) == len(self.test_pixels)
        
        # Each row should have exactly one interval (full width)
        for row_intervals in intervals:
            assert len(row_intervals) == 1
            assert row_intervals[0] == len(self.test_pixels[0])
    
    def test_get_interval_function(self):
        """Test getting interval functions by name."""
        # Test valid function names
        func = get_interval_function("random")
        assert func == random_intervals
        
        func = get_interval_function("threshold")
        assert func == threshold_intervals
        
        func = get_interval_function("waves")
        assert func == wave_intervals
        
        func = get_interval_function("none")
        assert func == no_intervals
        
        # Test invalid function name
        with pytest.raises((KeyError, Exception)):  # Custom exception or KeyError
            get_interval_function("invalid_function")
    
    def test_list_interval_functions(self):
        """Test listing available interval functions."""
        functions = list_interval_functions()
        assert isinstance(functions, list)
        assert len(functions) > 0
        assert "random" in functions
        assert "threshold" in functions
        assert "waves" in functions
        assert "none" in functions
    
    def test_interval_functions_registry(self):
        """Test the interval functions registry."""
        assert isinstance(INTERVAL_FUNCTIONS, dict)
        assert len(INTERVAL_FUNCTIONS) > 0
        
        # Test that all listed functions are in registry
        for name in list_interval_functions():
            assert name in INTERVAL_FUNCTIONS
            assert callable(INTERVAL_FUNCTIONS[name])
    
    def test_constants(self):
        """Test color constants."""
        assert BLACK_PIXEL == (0, 0, 0, 255)
        assert WHITE_PIXEL == (255, 255, 255, 255)
    
    def test_interval_function_signatures(self):
        """Test that interval functions have correct signatures."""
        # Test functions that should return intervals
        for func_name in ["random", "threshold", "waves", "none"]:
            func = get_interval_function(func_name)
            result = func(self.test_pixels, self.test_args)
            
            # Should return list of lists (intervals)
            assert isinstance(result, list)
            if len(result) > 0:
                assert isinstance(result[0], list)


class TestEdgeBasedIntervals:
    """Test class for edge-based interval functions that require image files."""
    
    def setup_method(self):
        """Set up test fixtures with actual image file."""
        # Use existing sample image
        sample_image_path = Path(__file__).parent.parent / "images" / "default.jpg"
        if sample_image_path.exists():
            self.test_args = {
                "url": str(sample_image_path),
                "internet": False,
                "angle": 0,
                "bottom_threshold": 0.2,
                "upper_threshold": 0.8
            }
            
            # Create small test pixel array
            self.test_pixels = [
                [(255, 0, 0, 255), (255, 0, 0, 255)],
                [(255, 0, 0, 255), (255, 0, 0, 255)]
            ]
        else:
            self.test_args = None
            self.test_pixels = None
    
    @pytest.mark.skipif(not Path(__file__).parent.parent.joinpath("images", "default.jpg").exists(),
                       reason="Sample image not available")
    def test_edge_intervals_with_sample(self):
        """Test edge intervals with sample image if available."""
        if self.test_args and self.test_pixels:
            # Import here to avoid issues if dependencies are missing
            from pixelsort.effects.interval_functions import edge_intervals
            
            try:
                intervals = edge_intervals(self.test_pixels, self.test_args)
                
                # Check basic structure
                assert isinstance(intervals, list)
                assert len(intervals) == len(self.test_pixels)
                
                for row_intervals in intervals:
                    assert isinstance(row_intervals, list)
                    if len(row_intervals) > 0:
                        assert row_intervals[-1] == len(self.test_pixels[0])
            except Exception as e:
                # If edge detection fails, just ensure it raises an appropriate error
                assert isinstance(e, (OSError, ValueError, ImportError))


if __name__ == "__main__":
    pytest.main([__file__])
