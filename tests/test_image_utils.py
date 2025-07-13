#!/usr/bin/env python3
"""
Tests for image utility functions.
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.utils.image_utils import (
    check_url_or_path, open_image, image_to_pixel_array,
    crop_to_reference, set_pixel, append_pixel_from_image,
    rotate_image, apply_edge_filter
)


class TestImageUtils:
    """Test class for image utility functions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary test image
        self.test_image = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.test_image.save(self.temp_file.name)
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_check_url_or_path_valid_file(self):
        """Test checking valid file path."""
        assert check_url_or_path(self.temp_file.name) is True
    
    def test_check_url_or_path_invalid_file(self):
        """Test checking invalid file path."""
        assert check_url_or_path("/nonexistent/path.png") is False
    
    def test_open_image_local_file(self):
        """Test opening local image file."""
        img = open_image(self.temp_file.name, has_internet=False)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"
        assert img.size == (10, 10)
    
    def test_open_image_invalid_file(self):
        """Test opening invalid image file."""
        with pytest.raises((SystemExit, Exception)):  # SystemExit or other exception
            open_image("/nonexistent/path.png", has_internet=False)
    
    def test_image_to_pixel_array(self):
        """Test converting image to pixel array."""
        # Create small test image
        test_img = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
        data = test_img.load()
        
        # Convert to pixel array
        pixels = image_to_pixel_array(2, 2, data, "Testing")
        
        # Verify structure
        assert len(pixels) == 2  # Height
        assert len(pixels[0]) == 2  # Width
        assert pixels[0][0] == (255, 0, 0, 255)  # Red pixel
    
    def test_crop_to_reference(self):
        """Test cropping image to reference size."""
        # Create larger image to crop
        large_img = Image.new("RGBA", (20, 20), (0, 255, 0, 255))
        reference_img = Image.new("RGBA", (10, 10), (0, 0, 255, 255))
        
        # Crop to reference
        cropped = crop_to_reference(large_img, reference_img)
        
        assert cropped.size == reference_img.size
        assert cropped.size == (10, 10)
    
    def test_set_pixel(self):
        """Test setting pixel in image."""
        # Create test image and pixel array
        test_img = Image.new("RGBA", (2, 2), (255, 255, 255, 255))
        pixel_data = [[(255, 0, 0, 255), (0, 255, 0, 255)], 
                     [(0, 0, 255, 255), (255, 255, 0, 255)]]
        
        # Set pixel
        set_pixel(test_img, 0, 0, pixel_data)
        
        # Verify pixel was set
        assert test_img.getpixel((0, 0)) == (255, 0, 0, 255)
    
    def test_append_pixel_from_image(self):
        """Test appending pixel from image data."""
        # Create test image
        test_img = Image.new("RGBA", (2, 2), (255, 0, 0, 255))
        data = test_img.load()
        
        # Create pixel list
        pixel_list = [[], []]
        
        # Append pixel
        append_pixel_from_image(pixel_list, 0, 0, data)
        
        assert len(pixel_list[0]) == 1
        assert pixel_list[0][0] == (255, 0, 0, 255)
    
    def test_rotate_image(self):
        """Test image rotation."""
        # Rotate 90 degrees
        rotated = rotate_image(self.test_image, 90)
        
        assert isinstance(rotated, Image.Image)
        # Size should be swapped for 90-degree rotation
        assert rotated.size == (10, 10)  # Square image, so same size
    
    def test_apply_edge_filter(self):
        """Test edge filter application."""
        # Apply edge filter
        edge_img = apply_edge_filter(self.test_image)
        
        assert isinstance(edge_img, Image.Image)
        assert edge_img.mode == "RGBA"
        assert edge_img.size == self.test_image.size


if __name__ == "__main__":
    pytest.main([__file__])
