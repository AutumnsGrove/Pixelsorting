"""
Gradio web interface for pixel sorting operations.

This module provides a user-friendly web interface for the pixel sorting application
using Gradio components. It integrates with the PixelSorter class to provide
real-time pixel sorting capabilities.
"""

import os
from typing import List
import gradio as gr

from .visualization_components import VisualizationComponents
from .image_processor import ImageProcessor
from .preset_manager import PresetManager
from .interface_components import InterfaceComponents
from .event_handlers import EventHandlers


class GradioInterface:
    """
    Gradio interface manager for the pixel sorting application.
    
    This refactored class delegates functionality to specialized modules:
    - VisualizationComponents for creating visual previews
    - ImageProcessor for image processing operations
    - PresetManager for preset management
    - InterfaceComponents for UI creation
    - EventHandlers for Gradio event bindings
    """

    def __init__(self):
        """Initialize the Gradio interface and all component modules."""
        # Get example images for the interface
        self.example_images = self._get_example_images()
        
        # Initialize all component modules
        self.visualization_components = VisualizationComponents()
        self.image_processor = ImageProcessor()
        self.preset_manager = PresetManager()
        self.interface_components = InterfaceComponents(self.example_images)
        
        # Event handlers will be initialized in create_interface()
        self.event_handlers = None

    def _get_example_images(self) -> List[str]:
        """
        Get list of example image paths.

        Returns:
            List of paths to example images
        """
        # Use the test image from the images/ folder instead of pre-sorted examples
        images_dir = os.path.join(os.path.dirname(__file__), "..", "..", "images")
        images_dir = os.path.abspath(images_dir)

        example_files = []
        if os.path.exists(images_dir):
            for filename in sorted(os.listdir(images_dir)):
                if filename.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
                ):
                    example_files.append(os.path.join(images_dir, filename))

        return example_files[:3]  # Limit to 3 examples for interface

    def create_interface(self) -> gr.Blocks:
        """
        Create and return the Gradio interface using modular components.

        Returns:
            Configured Gradio Blocks interface
        """
        # Load custom presets on interface creation
        self.preset_manager.load_custom_presets()
        
        # Create the main Gradio interface using InterfaceComponents
        with gr.Blocks(
            title="Pixel Sorter",
            theme=gr.themes.Origin(),
            css=".gradio-container {max-width: 1200px; margin: auto;}",
        ) as interface:

            # Create header
            gr.Markdown("# Pixel Sorter")
            gr.Markdown(
                "Upload an image and experiment with different pixel sorting effects. "
                "Adjust the parameters to create unique visual art!"
            )

            # Create all interface components using the modular component factory
            basic_components = self.interface_components.create_basic_tab()
            advanced_components = self.interface_components.create_advanced_tab()
            preset_components = self.interface_components.create_presets_tab()
            
            # Combine all components for easy access
            all_components = {**basic_components, **advanced_components, **preset_components}
            
            # Initialize event handlers with all components
            self.event_handlers = EventHandlers(
                components=all_components,
                visualization_components=self.visualization_components,
                image_processor=self.image_processor,
                preset_manager=self.preset_manager
            )
            
            # Set up all event handlers
            self.event_handlers.setup_events(interface)

            # Footer
            gr.Markdown(
                "---\n"
                "💡 **Tips:** Start with the basic options, then experiment with advanced parameters. "
                "Different combinations of interval and sorting functions create unique effects! "
                "For large images (>2MB), try scaling down to 25-50% for more visible effects and faster processing. "
                "When using 'file' or 'file-edges' functions, use the Preview CA button to see the cellular automata pattern first."
            )

        return interface


def create_interface() -> gr.Blocks:
    """
    Factory function to create a Gradio interface.

    Returns:
        Configured Gradio Blocks interface
    """
    gradio_interface = GradioInterface()
    return gradio_interface.create_interface()


def launch_interface(
    share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860
):
    """
    Launch the Gradio interface.

    Args:
        share: Whether to create a public link
        server_name: Server hostname
        server_port: Server port
    """
    interface = create_interface()
    interface.launch(
        share=share, server_name=server_name, server_port=server_port, show_error=True
    )