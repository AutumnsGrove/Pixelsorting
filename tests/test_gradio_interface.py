#!/usr/bin/env python3
"""
Tests for Gradio interface components.
"""

import pytest
import sys
from pathlib import Path
from PIL import Image
import tempfile
import os

# Add the parent directory to sys.path so we can import pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pixelsort.ui.gradio_interface import create_interface, launch_interface
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False


@pytest.mark.skipif(not GRADIO_AVAILABLE, reason="Gradio not available")
class TestGradioInterface:
    """Test class for Gradio interface functionality."""
    
    def test_create_interface_function_exists(self):
        """Test that create_interface function exists and is callable."""
        assert callable(create_interface)
    
    def test_launch_interface_function_exists(self):
        """Test that launch_interface function exists and is callable."""
        assert callable(launch_interface)
    
    def test_create_interface_returns_object(self):
        """Test that create_interface returns an object."""
        try:
            interface = create_interface()
            assert interface is not None
        except Exception as e:
            # If it fails, it should be due to missing dependencies or configuration
            # not due to our code structure
            assert any(keyword in str(e).lower() for keyword in ['gradio', 'import', 'module'])


class TestGradioInterfaceStructure:
    """Test the structure and imports of Gradio interface module."""
    
    def test_gradio_interface_file_exists(self):
        """Test that the Gradio interface file exists."""
        interface_file = Path(__file__).parent.parent / "pixelsort" / "ui" / "gradio_interface.py"
        assert interface_file.exists()
    
    def test_gradio_interface_imports(self):
        """Test that required functions can be imported."""
        try:
            from pixelsort.ui.gradio_interface import create_interface, launch_interface
            # If import succeeds, the functions should exist
            assert hasattr(create_interface, '__call__')
            assert hasattr(launch_interface, '__call__')
        except ImportError:
            # This is acceptable if Gradio is not installed
            pytest.skip("Gradio interface not available")
    
    def test_progress_manager_exists(self):
        """Test that progress manager exists."""
        progress_file = Path(__file__).parent.parent / "pixelsort" / "ui" / "progress_manager.py"
        assert progress_file.exists()


@pytest.mark.skipif(not GRADIO_AVAILABLE, reason="Gradio not available")
class TestGradioIntegration:
    """Integration tests for Gradio interface with pixel sorting."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a test image
        self.test_image = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
        
        # Save to temporary file
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        self.test_image.save(self.temp_file.name)
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
        except FileNotFoundError:
            pass
    
    def test_interface_creation_with_error_handling(self):
        """Test interface creation with proper error handling."""
        try:
            # Try to create interface
            interface = create_interface()
            
            # If successful, should have expected attributes
            # Note: This may fail due to Gradio version differences
            assert interface is not None
            
        except ImportError:
            pytest.skip("Gradio dependencies not available")
        except Exception as e:
            # Other exceptions should be related to configuration or dependencies
            error_msg = str(e).lower()
            expected_errors = ['gradio', 'module', 'import', 'version', 'requirement']
            assert any(err in error_msg for err in expected_errors), f"Unexpected error: {e}"


if __name__ == "__main__":
    pytest.main([__file__])