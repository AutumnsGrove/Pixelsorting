"""
Event handlers for the pixel sorting Gradio interface.

This module contains all the Gradio event binding logic extracted from the GradioInterface class,
organized into a clean EventHandlers class that manages component interactions and delegates
functionality to appropriate modules.
"""

from typing import Dict, Any
import gradio as gr

from .visualization_components import VisualizationComponents
from .image_processor import ImageProcessor
from .preset_manager import PresetManager


class EventHandlers:
    """
    Event handler manager for the pixel sorting Gradio interface.
    
    This class handles all Gradio event bindings including click handlers,
    change handlers, and load handlers. It delegates actual functionality
    to the appropriate specialized modules.
    """

    def __init__(
        self,
        components: Dict[str, Any],
        visualization_components: VisualizationComponents,
        image_processor: ImageProcessor,
        preset_manager: PresetManager
    ):
        """
        Initialize the event handlers.
        
        Args:
            components: Dictionary of all UI components from InterfaceComponents
            visualization_components: Instance of VisualizationComponents for visualizations
            image_processor: Instance of ImageProcessor for image processing
            preset_manager: Instance of PresetManager for preset operations
        """
        self.components = components
        self.visualization_components = visualization_components
        self.image_processor = image_processor
        self.preset_manager = preset_manager

    def setup_events(self, interface: gr.Blocks) -> None:
        """
        Set up all event handlers for the interface.
        
        Args:
            interface: The Gradio Blocks interface to bind events to
        """
        # Set up CA preview functionality
        self._setup_ca_preview_events()
        
        # Set up visualization events
        self._setup_visualization_events(interface)
        
        # Set up threshold events
        self._setup_threshold_events(interface)
        
        # Set up dimension display events
        self._setup_dimension_events()
        
        # Set up preset events
        self._setup_preset_events()
        
        # Set up main processing event
        self._setup_processing_events()

    def _setup_ca_preview_events(self) -> None:
        """Set up cellular automata preview events."""
        self.components['ca_preview_button'].click(
            fn=self.visualization_components.preview_cellular_automata,
            inputs=[self.components['ca_rule_slider']],
            outputs=[self.components['ca_preview_image']],
            show_progress=False,
        )

    def _setup_visualization_events(self, interface: gr.Blocks) -> None:
        """Set up visualization events for angle and sorting function previews."""
        # Set up the angle visualization (updates in real-time as slider moves)
        self.components['angle_slider'].change(
            fn=self.visualization_components.create_angle_visualization,
            inputs=[self.components['angle_slider']],
            outputs=[self.components['angle_visualization']],
            show_progress=False,
        )

        # Initialize angle visualization with default value
        interface.load(
            fn=self.visualization_components.create_angle_visualization,
            inputs=[self.components['angle_slider']],
            outputs=[self.components['angle_visualization']],
        )
        
        # Set up the sorting function visualization (updates in real-time as dropdown changes)
        self.components['sorting_dropdown'].change(
            fn=self.visualization_components.create_sorting_function_visualization,
            inputs=[self.components['sorting_dropdown']],
            outputs=[self.components['sorting_visualization']],
            show_progress=False,
        )
        
        # Initialize sorting function visualization with default value
        interface.load(
            fn=self.visualization_components.create_sorting_function_visualization,
            inputs=[self.components['sorting_dropdown']],
            outputs=[self.components['sorting_visualization']],
        )

    def _setup_threshold_events(self, interface: gr.Blocks) -> None:
        """Set up threshold visualization and overlay events."""
        # Set up the threshold visualization (updates in real-time as sliders move)
        self.components['bottom_threshold_slider'].change(
            fn=self.visualization_components.create_threshold_visualization,
            inputs=[self.components['bottom_threshold_slider'], self.components['upper_threshold_slider']],
            outputs=[self.components['threshold_visualization']],
            show_progress=False,
        )
        
        self.components['upper_threshold_slider'].change(
            fn=self.visualization_components.create_threshold_visualization,
            inputs=[self.components['bottom_threshold_slider'], self.components['upper_threshold_slider']],
            outputs=[self.components['threshold_visualization']],
            show_progress=False,
        )
        
        # Initialize threshold visualization with default values
        interface.load(
            fn=self.visualization_components.create_threshold_visualization,
            inputs=[self.components['bottom_threshold_slider'], self.components['upper_threshold_slider']],
            outputs=[self.components['threshold_visualization']],
        )
        
        # Set up the threshold overlay (updates when sliders change or image changes)
        self.components['bottom_threshold_slider'].change(
            fn=self.visualization_components.create_threshold_overlay,
            inputs=[
                self.components['input_image'], 
                self.components['bottom_threshold_slider'], 
                self.components['upper_threshold_slider'], 
                self.components['overlay_toggle']
            ],
            outputs=[self.components['threshold_overlay_image']],
            show_progress=False,
        )
        
        self.components['upper_threshold_slider'].change(
            fn=self.visualization_components.create_threshold_overlay,
            inputs=[
                self.components['input_image'], 
                self.components['bottom_threshold_slider'], 
                self.components['upper_threshold_slider'], 
                self.components['overlay_toggle']
            ],
            outputs=[self.components['threshold_overlay_image']],
            show_progress=False,
        )
        
        self.components['overlay_toggle'].change(
            fn=self.visualization_components.create_threshold_overlay,
            inputs=[
                self.components['input_image'], 
                self.components['bottom_threshold_slider'], 
                self.components['upper_threshold_slider'], 
                self.components['overlay_toggle']
            ],
            outputs=[self.components['threshold_overlay_image']],
            show_progress=False,
        )
        
        # Update overlay when input image changes
        self.components['input_image'].change(
            fn=self.visualization_components.create_threshold_overlay,
            inputs=[
                self.components['input_image'], 
                self.components['bottom_threshold_slider'], 
                self.components['upper_threshold_slider'], 
                self.components['overlay_toggle']
            ],
            outputs=[self.components['threshold_overlay_image']],
            show_progress=False,
        )
        
        # Initialize threshold overlay with default values
        interface.load(
            fn=self.visualization_components.create_threshold_overlay,
            inputs=[
                self.components['input_image'], 
                self.components['bottom_threshold_slider'], 
                self.components['upper_threshold_slider'], 
                self.components['overlay_toggle']
            ],
            outputs=[self.components['threshold_overlay_image']],
        )

    def _setup_dimension_events(self) -> None:
        """Set up dimension display events for image scaling."""
        # Set up dimension display updates when image or scale changes
        self.components['input_image'].change(
            fn=self.image_processor.calculate_scaled_dimensions,
            inputs=[self.components['input_image'], self.components['scale_slider']],
            outputs=[self.components['scale_info']],
            show_progress=False,
        )
        
        self.components['scale_slider'].change(
            fn=self.image_processor.calculate_scaled_dimensions,
            inputs=[self.components['input_image'], self.components['scale_slider']],
            outputs=[self.components['scale_info']],
            show_progress=False,
        )

    def _setup_preset_events(self) -> None:
        """Set up preset loading and saving events."""
        # Set up preset loading functionality
        self.components['load_preset_button'].click(
            fn=self.preset_manager.load_preset_values,
            inputs=[self.components['preset_dropdown']],
            outputs=[
                self.components['interval_dropdown'],
                self.components['sorting_dropdown'],
                self.components['randomness_slider'],
                self.components['angle_slider'],
                self.components['bottom_threshold_slider'],
                self.components['upper_threshold_slider'],
                self.components['characteristic_length_slider'],
                self.components['ca_rule_slider'],
                self.components['preset_status']
            ],
            show_progress=False,
        )
        
        # Set up preset saving functionality
        self.components['save_preset_button'].click(
            fn=self.preset_manager.save_current_as_preset,
            inputs=[
                self.components['new_preset_name'],
                self.components['interval_dropdown'],
                self.components['sorting_dropdown'],
                self.components['randomness_slider'],
                self.components['angle_slider'],
                self.components['bottom_threshold_slider'],
                self.components['upper_threshold_slider'],
                self.components['characteristic_length_slider'],
                self.components['ca_rule_slider']
            ],
            outputs=[self.components['preset_dropdown'], self.components['save_preset_status']],
            show_progress=False,
        )

    def _setup_processing_events(self) -> None:
        """Set up the main image processing events."""
        # Set up the processing function
        self.components['process_button'].click(
            fn=self.image_processor.process_image_gradio,
            inputs=[
                self.components['input_image'],
                self.components['interval_dropdown'],
                self.components['sorting_dropdown'],
                self.components['angle_slider'],
                self.components['randomness_slider'],
                self.components['bottom_threshold_slider'],
                self.components['upper_threshold_slider'],
                self.components['characteristic_length_slider'],
                self.components['ca_rule_slider'],
                self.components['scale_slider'],
            ],
            outputs=[self.components['output_image'], self.components['status_text']],
            show_progress=True,
        )