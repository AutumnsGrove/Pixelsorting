#!/usr/bin/env python3
"""Basic tests for pixelsort package."""

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_package_import():
    """Test that the pixelsort package can be imported."""
    try:
        import pixelsort
        assert True
    except ImportError:
        pytest.fail("Failed to import pixelsort package")


def test_config_directory_exists():
    """Test that config directory exists."""
    config_dir = Path(__file__).parent.parent / "config"
    assert config_dir.exists(), "Config directory should exist"
    assert config_dir.is_dir(), "Config path should be a directory"


def test_output_directory_exists():
    """Test that output directory exists."""
    output_dir = Path(__file__).parent.parent / "output"
    assert output_dir.exists(), "Output directory should exist"
    assert output_dir.is_dir(), "Output path should be a directory"


def test_images_directory_exists():
    """Test that images directory exists."""
    images_dir = Path(__file__).parent.parent / "images"
    assert images_dir.exists(), "Images directory should exist"
    assert images_dir.is_dir(), "Images path should be a directory"


if __name__ == "__main__":
    pytest.main([__file__])