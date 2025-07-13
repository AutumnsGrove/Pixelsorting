"""
Main entry point for the pixel sorting application.

This module provides the main function to launch the Gradio web interface.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from pixelsort
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixelsort.ui.gradio_interface import launch_interface


def main():
    """
    Main function to launch the pixel sorting web interface.
    """
    print("🎨 Starting Pixel Sorter Web Interface...")
    print("📂 Loading components...")
    
    try:
        # Launch the interface
        launch_interface(
            share=False,  # Set to True to create a public link
            server_name="127.0.0.1",
            server_port=7860
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Pixel Sorter. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting interface: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()