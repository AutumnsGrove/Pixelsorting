"""
Gradio web interface for pixel sorting operations.

This module provides a user-friendly web interface for the pixel sorting application
using Gradio components. It integrates with the PixelSorter class to provide
real-time pixel sorting capabilities.
"""

import os
from typing import Optional, Tuple, List
import gradio as gr
from PIL import Image

from ..core.processor import PixelSorter
from ..effects.sorting_functions import list_sorting_functions
from ..effects.interval_functions import list_interval_functions
from ..effects.special_effects import generate_elementary_cellular_automata
from ..utils.config import SortingConfig, validate_config
from .progress_manager import ProgressManager


class GradioInterface:
    """
    Gradio interface manager for the pixel sorting application.
    """
    
    def __init__(self):
        """Initialize the Gradio interface."""
        self.current_processor: Optional[PixelSorter] = None
        self.example_images = self._get_example_images()
        
    def _get_example_images(self) -> List[str]:
        """
        Get list of example image paths.
        
        Returns:
            List of paths to example images
        """
        examples_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'examples')
        examples_dir = os.path.abspath(examples_dir)
        
        example_files = []
        if os.path.exists(examples_dir):
            for filename in sorted(os.listdir(examples_dir)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    example_files.append(os.path.join(examples_dir, filename))
        
        return example_files[:3]  # Limit to 3 examples for interface
    
    def preview_cellular_automata(self, ca_rule_number: int) -> Image.Image:
        """
        Generate a preview of the cellular automata pattern.
        
        Args:
            ca_rule_number: CA rule number (-1 for random, 0-255 for specific)
            
        Returns:
            PIL Image showing the CA pattern
        """
        try:
            # Use a fixed preview size for fast generation
            preview_width = 400
            preview_height = 300
            
            rule_number = ca_rule_number if ca_rule_number != -1 else None
            ca_image = generate_elementary_cellular_automata(
                preview_width, preview_height, rule_number
            )
            
            return ca_image
            
        except Exception as e:
            print(f"Error generating CA preview: {e}")
            # Return a simple placeholder image on error
            placeholder = Image.new("RGB", (400, 300), color=(128, 128, 128))
            return placeholder
    
    def process_image_gradio(
        self,
        image: Image.Image,
        interval_function: str,
        sorting_function: str,
        angle: float,
        randomness: float,
        bottom_threshold: float,
        upper_threshold: float,
        characteristic_length: int,
        ca_rule_number: int,
        progress: gr.Progress = gr.Progress()
    ) -> Tuple[Image.Image, str]:
        """
        Process an image using Gradio progress tracking.
        
        Args:
            image: Input PIL Image
            interval_function: Name of interval function
            sorting_function: Name of sorting function  
            angle: Rotation angle in degrees
            randomness: Randomness percentage (0-100)
            bottom_threshold: Lower threshold for threshold interval function
            upper_threshold: Upper threshold for threshold interval function
            characteristic_length: Characteristic length for random intervals
            progress: Gradio progress tracker
            
        Returns:
            Tuple of (processed image, status message)
        """
        try:
            # Initialize progress manager with step weights
            progress_manager = ProgressManager(progress)
            progress_manager.set_steps({
                "validation": 0.05,
                "initialization": 0.1,
                "preparation": 0.2,
                "interval_generation": 0.3,
                "pixel_sorting": 0.25,
                "reconstruction": 0.1
            })
            
            # Step 1: Validate configuration
            progress_manager.start_step("validation", "Validating configuration...")
            
            config = SortingConfig(
                bottom_threshold=bottom_threshold,
                upper_threshold=upper_threshold,
                clength=characteristic_length,
                randomness=randomness,
                angle=angle,
                ca_rule_number=ca_rule_number if ca_rule_number != -1 else None,
                interval_function=interval_function,
                sorting_function=sorting_function,
                url="",  # Using uploaded image
                internet=False
            )
            
            validate_config(config)
            progress_manager.complete_step("validation", "Configuration validated")
            
            # Step 2: Initialize processor
            progress_manager.start_step("initialization", "Initializing processor...")
            
            # Get config dict and remove duplicated parameters
            config_dict = config.to_dict()
            config_dict.pop('int_function', None)  # Remove interval_function from dict
            config_dict.pop('sorting_function', None)  # Remove sorting_function from dict
            
            self.current_processor = PixelSorter(
                interval_function=interval_function,
                sorting_function=sorting_function,
                **config_dict
            )
            progress_manager.complete_step("initialization", "Processor initialized")
            
            # Step 3: Prepare image
            progress_manager.start_step("preparation", "Preparing image...")
            
            # Save uploaded image temporarily for processing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                image.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            try:
                # Process the image with detailed progress tracking
                self.current_processor.prepare_image(tmp_path, internet=False)
                progress_manager.complete_step("preparation", "Image prepared")
                
                # Step 4: Generate intervals
                progress_manager.start_step("interval_generation", "Analyzing image structure...")
                self.current_processor.generate_intervals()
                progress_manager.complete_step("interval_generation", "Intervals generated")
                
                # Step 5: Sort pixels
                progress_manager.start_step("pixel_sorting", "Sorting pixels...")
                self.current_processor.sort_pixels()
                progress_manager.complete_step("pixel_sorting", "Pixels sorted")
                
                # Step 6: Reconstruct image
                progress_manager.start_step("reconstruction", "Building final image...")
                result_image = self.current_processor.reconstruct_image()
                progress_manager.complete_step("reconstruction", "Processing complete!")
                
                # Get processing info for status message
                info = self.current_processor.get_processing_info()
                status_msg = (
                    f"✅ Processing complete! "
                    f"Used '{info['interval_function']}' intervals with '{info['sorting_function']}' sorting. "
                    f"Original: {info['original_size']}, "
                    f"Output: {info['output_size']}"
                )
                
                return result_image, status_msg
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                
        except Exception as e:
            error_msg = f"❌ Error processing image: {str(e)}"
            print(f"Processing error: {e}")  # For debugging
            
            # Update progress to show error
            if 'progress' in locals():
                progress(1.0, desc="Error occurred")
                
            # Return original image with error message
            return image, error_msg
    
    def create_interface(self) -> gr.Blocks:
        """
        Create and return the Gradio interface.
        
        Returns:
            Configured Gradio Blocks interface
        """
        # Get available functions
        interval_functions = list_interval_functions()
        sorting_functions = list_sorting_functions()
        
        with gr.Blocks(
            title="Pixel Sorter",
            theme=gr.themes.Glass(),
            css=".gradio-container {max-width: 1200px; margin: auto;}"
        ) as interface:
            
            gr.Markdown("# 🎨 Pixel Sorter")
            gr.Markdown(
                "Upload an image and experiment with different pixel sorting effects. "
                "Adjust the parameters to create unique visual art!"
            )
            
            with gr.Tab("Basic Options"):
                with gr.Row():
                    with gr.Column(scale=1):
                        input_image = gr.Image(
                            type="pil",
                            label="Upload Image",
                            height=400
                        )
                        
                        # Example images
                        if self.example_images:
                            gr.Examples(
                                examples=self.example_images,
                                inputs=input_image,
                                label="Try these examples:"
                            )
                    
                    with gr.Column(scale=1):
                        output_image = gr.Image(
                            type="pil", 
                            label="Sorted Image",
                            height=400
                        )
                        
                        status_text = gr.Textbox(
                            label="Status",
                            placeholder="Upload an image and click 'Sort Pixels' to begin...",
                            interactive=False
                        )
                
                with gr.Row():
                    interval_dropdown = gr.Dropdown(
                        choices=interval_functions,
                        value="random",
                        label="Interval Function",
                        info="How to group pixels for sorting"
                    )
                    sorting_dropdown = gr.Dropdown(
                        choices=sorting_functions,
                        value="lightness",
                        label="Sorting Function", 
                        info="How to sort pixels within each group"
                    )
                
                with gr.Row():
                    randomness_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=10,
                        step=1,
                        label="Randomness %",
                        info="Percentage of intervals to leave unsorted"
                    )
                    angle_slider = gr.Slider(
                        minimum=0,
                        maximum=359,
                        value=0,
                        step=1,
                        label="Rotation Angle",
                        info="Rotate image before sorting (degrees)"
                    )
            
            with gr.Tab("Advanced Options"):
                gr.Markdown("### Threshold Parameters")
                gr.Markdown("These parameters control the threshold interval function.")
                
                with gr.Row():
                    bottom_threshold_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.25,
                        step=0.01,
                        label="Bottom Threshold",
                        info="Lower lightness threshold for interval detection"
                    )
                    upper_threshold_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.8,
                        step=0.01,
                        label="Upper Threshold", 
                        info="Upper lightness threshold for interval detection"
                    )
                
                gr.Markdown("### Interval Parameters")
                characteristic_length_slider = gr.Slider(
                    minimum=1,
                    maximum=200,
                    value=50,
                    step=1,
                    label="Characteristic Length",
                    info="Base length for random and wave intervals"
                )
                
                gr.Markdown("### Cellular Automata Parameters")
                gr.Markdown("These parameters are used when 'file' or 'file-edges' interval functions are selected.")
                
                with gr.Row():
                    ca_rule_slider = gr.Slider(
                        minimum=-1,
                        maximum=255,
                        value=-1,
                        step=1,
                        label="CA Rule Number",
                        info="Cellular automata rule (0-255). Use -1 for random selection from recommended rules.",
                        scale=3
                    )
                    ca_preview_button = gr.Button(
                        "🔍 Preview CA",
                        size="sm",
                        scale=1
                    )
                
                ca_preview_image = gr.Image(
                    label="Cellular Automata Preview",
                    type="pil",
                    height=200,
                    visible=True,
                    interactive=False
                )
                
                with gr.Accordion("Recommended CA Rules", open=False):
                    gr.Markdown("""
                    **Recommended elementary cellular automata rules for interesting patterns:**
                    - **Rule 26, 19, 23, 25**: Simple patterns with structure
                    - **Rule 35, 106, 11**: More complex organized patterns  
                    - **Rule 110**: Turing complete, creates complex structures
                    - **Rule 45, 41, 105**: Irregular but structured patterns
                    - **Rule 54, 3, 15, 9**: Various geometric patterns
                    - **Rule 154, 142**: Dense, fractal-like patterns
                    
                    Set to -1 to randomly select from these recommended rules, or choose a specific number 0-255.
                    """)
                
                # Function descriptions
                gr.Markdown("### Function Descriptions")
                
                with gr.Accordion("Interval Functions", open=False):
                    gr.Markdown("""
                    - **random**: Creates intervals of random lengths
                    - **threshold**: Creates intervals based on pixel lightness thresholds  
                    - **edges**: Uses edge detection to determine intervals
                    - **waves**: Creates wave-like intervals with slight randomization
                    - **none**: No intervals (sorts entire rows)
                    - **file**: Uses cellular automata patterns as interval masks
                    - **file-edges**: Uses edge detection on cellular automata patterns
                    - **snap**: Thanos snap effect (removes ~50% of pixels randomly)
                    - **shuffle-total**: Shuffles pixels within each row
                    - **shuffle-axis**: Shuffles the order of rows vertically
                    """)
                
                with gr.Accordion("Sorting Functions", open=False):
                    gr.Markdown("""
                    - **lightness**: Sort by HSV lightness value
                    - **intensity**: Sort by sum of RGB values
                    - **hue**: Sort by HSV hue value
                    - **saturation**: Sort by HSV saturation value
                    - **red/green/blue**: Sort by individual color channels
                    - **minimum/maximum**: Sort by min/max RGB values
                    """)
            
            # Processing button
            process_button = gr.Button(
                "🎨 Sort Pixels",
                variant="primary",
                size="lg"
            )
            
            # Set up the CA preview function
            ca_preview_button.click(
                fn=self.preview_cellular_automata,
                inputs=[ca_rule_slider],
                outputs=[ca_preview_image],
                show_progress=False
            )
            
            # Set up the processing function
            process_button.click(
                fn=self.process_image_gradio,
                inputs=[
                    input_image,
                    interval_dropdown,
                    sorting_dropdown,
                    angle_slider,
                    randomness_slider,
                    bottom_threshold_slider,
                    upper_threshold_slider,
                    characteristic_length_slider,
                    ca_rule_slider
                ],
                outputs=[output_image, status_text],
                show_progress=True
            )
            
            # Footer
            gr.Markdown(
                "---\n"
                "💡 **Tips:** Start with the basic options, then experiment with advanced parameters. "
                "Different combinations of interval and sorting functions create unique effects! "
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


def launch_interface(share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860):
    """
    Launch the Gradio interface.
    
    Args:
        share: Whether to create a public link
        server_name: Server hostname
        server_port: Server port
    """
    interface = create_interface()
    interface.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        show_error=True
    )