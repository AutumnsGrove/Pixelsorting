#!/usr/bin/env python3
"""
Test script for the Gradio interface.

This script tests the basic functionality of the Gradio interface
without actually launching the web server.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from pixelsort.ui.gradio_interface import GradioInterface
from pixelsort.effects.sorting_functions import list_sorting_functions
from pixelsort.effects.interval_functions import list_interval_functions
from pixelsort.utils.config import SortingConfig, validate_config


def test_imports():
    """Test that all required imports work."""
    print("🧪 Testing imports...")
    
    try:
        import gradio as gr
        print("✅ Gradio imported successfully")
    except ImportError:
        print("❌ Gradio not available - install with: pip install gradio")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL imported successfully")
    except ImportError:
        print("❌ PIL not available")
        return False
    
    return True


def test_functions():
    """Test that function registries work."""
    print("\n🧪 Testing function registries...")
    
    sorting_funcs = list_sorting_functions()
    interval_funcs = list_interval_functions()
    
    print(f"✅ Found {len(sorting_funcs)} sorting functions: {sorting_funcs}")
    print(f"✅ Found {len(interval_funcs)} interval functions: {interval_funcs}")
    
    return len(sorting_funcs) > 0 and len(interval_funcs) > 0


def test_config():
    """Test configuration validation."""
    print("\n🧪 Testing configuration...")
    
    try:
        config = SortingConfig(
            bottom_threshold=0.25,
            upper_threshold=0.8,
            clength=50,
            randomness=10.0,
            angle=0.0
        )
        
        validate_config(config)
        print("✅ Configuration validation works")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_interface_creation():
    """Test interface creation."""
    print("\n🧪 Testing interface creation...")
    
    try:
        interface_manager = GradioInterface()
        print("✅ GradioInterface created successfully")
        
        # Test example image discovery
        examples = interface_manager._get_example_images()
        print(f"✅ Found {len(examples)} example images")
        
        return True
        
    except Exception as e:
        print(f"❌ Interface creation failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🎨 Testing Pixel Sorter Gradio Interface\n")
    
    tests = [
        ("Imports", test_imports),
        ("Function Registries", test_functions),
        ("Configuration", test_config),
        ("Interface Creation", test_interface_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The interface should work correctly.")
        print("\n🚀 To launch the interface, run:")
        print("   python pixelsort/main.py")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())