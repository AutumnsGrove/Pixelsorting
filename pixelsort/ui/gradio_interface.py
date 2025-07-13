"""
Gradio web interface for pixel sorting operations.

This module provides a user-friendly web interface for the pixel sorting application
using Gradio components. It integrates with the PixelSorter class to provide
real-time pixel sorting capabilities.
"""

import os
import math
from typing import Optional, Tuple, List
import gradio as gr
from PIL import Image, ImageDraw

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

    def create_angle_visualization(self, angle: float) -> Image.Image:
        """
        Create a visual representation of the rotation angle.

        Args:
            angle: Rotation angle in degrees (0-359)

        Returns:
            PIL Image showing a circle with a line indicating the angle
        """
        try:
            # Create a small square image
            size = 120
            img = Image.new("RGB", (size, size), color=(240, 240, 240))
            draw = ImageDraw.Draw(img)

            # Calculate center and radius
            center_x = center_y = size // 2
            radius = 45

            # Draw outer circle
            circle_bbox = [
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
            ]
            draw.ellipse(circle_bbox, outline=(100, 100, 100), width=2)

            # Draw center dot
            dot_radius = 3
            dot_bbox = [
                center_x - dot_radius,
                center_y - dot_radius,
                center_x + dot_radius,
                center_y + dot_radius,
            ]
            draw.ellipse(dot_bbox, fill=(100, 100, 100))

            # Convert angle to radians (subtract 90 to make 0° point up)
            angle_rad = math.radians(angle - 90)

            # Calculate line end point
            end_x = center_x + radius * 0.8 * math.cos(angle_rad)
            end_y = center_y + radius * 0.8 * math.sin(angle_rad)

            # Draw angle line
            draw.line([center_x, center_y, end_x, end_y], fill=(220, 50, 50), width=3)

            # Draw angle markers at 0°, 90°, 180°, 270°
            marker_angles = [0, 90, 180, 270]
            for marker_angle in marker_angles:
                marker_rad = math.radians(marker_angle - 90)
                marker_x = center_x + radius * 1.1 * math.cos(marker_rad)
                marker_y = center_y + radius * 1.1 * math.sin(marker_rad)

                # Draw small marker dots
                marker_dot_radius = 2
                marker_bbox = [
                    marker_x - marker_dot_radius,
                    marker_y - marker_dot_radius,
                    marker_x + marker_dot_radius,
                    marker_y + marker_dot_radius,
                ]
                draw.ellipse(marker_bbox, fill=(150, 150, 150))

            # Add angle text
            angle_text = f"{angle:.0f}°"
            # Use a simple text approach (PIL's text rendering is basic)
            text_bbox = draw.textbbox((0, 0), angle_text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = center_x - text_width // 2
            text_y = size - 25  # Move text up by 5 pixels

            draw.text((text_x, text_y), angle_text, fill=(50, 50, 50))

            return img

        except Exception as e:
            print(f"Error creating angle visualization: {e}")
            # Return a simple placeholder
            placeholder = Image.new("RGB", (120, 120), color=(200, 200, 200))
            return placeholder

    def create_threshold_visualization(self, bottom_threshold: float, upper_threshold: float) -> Image.Image:
        """
        Create a visual representation of the threshold settings.
        
        Args:
            bottom_threshold: Lower threshold value (0.0-1.0)
            upper_threshold: Upper threshold value (0.0-1.0)
            
        Returns:
            PIL Image showing a lightness gradient with threshold ranges highlighted
        """
        try:
            # Create image dimensions
            width = 300
            height = 80
            img = Image.new("RGB", (width, height), color=(250, 250, 250))
            draw = ImageDraw.Draw(img)
            
            # Draw background gradient from black to white
            gradient_height = 40
            gradient_y = 15
            
            for x in range(width):
                lightness = x / (width - 1)  # 0.0 to 1.0
                gray_value = int(lightness * 255)
                color = (gray_value, gray_value, gray_value)
                
                draw.line([x, gradient_y, x, gradient_y + gradient_height], fill=color)
            
            # Draw border around gradient
            draw.rectangle([0, gradient_y, width-1, gradient_y + gradient_height], 
                         outline=(100, 100, 100), width=1)
            
            # Calculate positions for threshold markers
            bottom_x = int(bottom_threshold * (width - 1))
            upper_x = int(upper_threshold * (width - 1))
            
            # Draw threshold range highlights
            # Pixels BELOW bottom threshold will be sorted (red overlay)
            if bottom_threshold > 0:
                for x in range(0, bottom_x + 1):
                    for y in range(gradient_y, gradient_y + gradient_height):
                        # Get existing pixel and blend with red
                        existing = img.getpixel((x, y))
                        blended = (
                            min(255, existing[0] + 80),  # Add red
                            max(0, existing[1] - 20),    # Reduce green
                            max(0, existing[2] - 20)     # Reduce blue
                        )
                        img.putpixel((x, y), blended)
            
            # Pixels ABOVE upper threshold will be sorted (blue overlay)
            if upper_threshold < 1.0:
                for x in range(upper_x, width):
                    for y in range(gradient_y, gradient_y + gradient_height):
                        # Get existing pixel and blend with blue
                        existing = img.getpixel((x, y))
                        blended = (
                            max(0, existing[0] - 20),    # Reduce red
                            max(0, existing[1] - 20),    # Reduce green
                            min(255, existing[2] + 80)   # Add blue
                        )
                        img.putpixel((x, y), blended)
            
            # Draw threshold markers
            marker_height = 15
            
            # Bottom threshold marker (red)
            draw.line([bottom_x, gradient_y - marker_height, bottom_x, gradient_y + gradient_height + marker_height], 
                     fill=(220, 50, 50), width=2)
            
            # Upper threshold marker (blue)
            draw.line([upper_x, gradient_y - marker_height, upper_x, gradient_y + gradient_height + marker_height], 
                     fill=(50, 50, 220), width=2)
            
            # Add labels
            draw.text((5, 2), "Dark", fill=(50, 50, 50))
            draw.text((width - 35, 2), "Light", fill=(50, 50, 50))
            
            # Add threshold values
            bottom_text = f"Lower: {bottom_threshold:.2f}"
            upper_text = f"Upper: {upper_threshold:.2f}"
            
            draw.text((5, height - 15), bottom_text, fill=(220, 50, 50))
            draw.text((width - 80, height - 15), upper_text, fill=(50, 50, 220))
            
            # Add explanation in middle
            explanation = "Colored areas will be sorted"
            text_bbox = draw.textbbox((0, 0), explanation)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = (width - text_width) // 2
            draw.text((text_x, height - 15), explanation, fill=(80, 80, 80))
            
            return img
            
        except Exception as e:
            print(f"Error creating threshold visualization: {e}")
            # Return a simple placeholder
            placeholder = Image.new("RGB", (300, 80), color=(200, 200, 200))
            return placeholder

    def calculate_scaled_dimensions(self, image: Image.Image, scale_percent: float) -> str:
        """
        Calculate and format the dimensions after scaling.
        
        Args:
            image: Input PIL Image or None
            scale_percent: Scale percentage (10-100)
            
        Returns:
            Formatted string with scaled dimensions and size info
        """
        if image is None:
            return "Upload an image to see dimensions"
        
        try:
            original_width, original_height = image.size
            scale_factor = scale_percent / 100.0
            
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Calculate approximate file size reduction
            size_reduction = int((1 - scale_factor * scale_factor) * 100)
            
            if scale_percent == 100:
                return f"Original: {original_width}×{original_height}"
            else:
                return f"Scaled: {new_width}×{new_height} ({scale_percent}% scale, ~{size_reduction}% smaller)"
                
        except Exception as e:
            return "Error calculating dimensions"

    def scale_image(self, image: Image.Image, scale_percent: float) -> Image.Image:
        """
        Scale an image while preserving aspect ratio.
        
        Args:
            image: Input PIL Image
            scale_percent: Scale percentage (10-100)
            
        Returns:
            Scaled PIL Image
        """
        if scale_percent >= 100:
            return image  # No scaling needed
        
        try:
            scale_factor = scale_percent / 100.0
            original_width, original_height = image.size
            
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            # Use high-quality resampling
            scaled_image = image.resize((new_width, new_height), Image.LANCZOS)
            return scaled_image
            
        except Exception as e:
            print(f"Error scaling image: {e}")
            return image  # Return original if scaling fails

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
        scale_percent: float,
        progress: gr.Progress = gr.Progress(),
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
            progress_manager.set_steps(
                {
                    "validation": 0.05,
                    "initialization": 0.1,
                    "preparation": 0.2,
                    "interval_generation": 0.3,
                    "pixel_sorting": 0.25,
                    "reconstruction": 0.1,
                }
            )

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
                internet=False,
            )

            validate_config(config)
            progress_manager.complete_step("validation", "Configuration validated")

            # Step 2: Prepare image and initialize processor  
            progress_manager.start_step("preparation", "Preparing image...")

            # Scale the image if requested
            if scale_percent < 100:
                image = self.scale_image(image, scale_percent)
                print(f"Scaled image to {scale_percent}% ({image.size[0]}×{image.size[1]})")

            # Save (potentially scaled) image temporarily for processing
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                image.save(tmp_file.name)
                tmp_path = tmp_file.name

            # Get config dict and remove duplicated parameters
            config_dict = config.to_dict()
            config_dict.pop("int_function", None)  # Remove interval_function from dict
            config_dict.pop("sorting_function", None)  # Remove sorting_function from dict
            
            # Update config with the actual file path for interval functions that need to reload the image
            config_dict['url'] = tmp_path
            config_dict['internet'] = False

            # Initialize processor with correct file path
            self.current_processor = PixelSorter(
                interval_function=interval_function,
                sorting_function=sorting_function,
                **config_dict,
            )

            try:
                # Process the image with detailed progress tracking
                self.current_processor.prepare_image(tmp_path, internet=False)
                progress_manager.complete_step("preparation", "Image prepared")

                # Step 4: Generate intervals
                progress_manager.start_step(
                    "interval_generation", "Analyzing image structure..."
                )
                self.current_processor.generate_intervals()
                progress_manager.complete_step(
                    "interval_generation", "Intervals generated"
                )

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
            if "progress" in locals():
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
            css=".gradio-container {max-width: 1200px; margin: auto;}",
        ) as interface:

            gr.Markdown("# Pixel Sorter")
            gr.Markdown(
                "Upload an image and experiment with different pixel sorting effects. "
                "Adjust the parameters to create unique visual art!"
            )

            with gr.Tab("Basic Options"):
                with gr.Row():
                    with gr.Column(scale=1):
                        input_image = gr.Image(
                            type="pil", label="Upload Image", height=400
                        )

                        # Example images
                        if self.example_images:
                            gr.Examples(
                                examples=self.example_images,
                                inputs=input_image,
                                label="Try these examples:",
                            )

                    with gr.Column(scale=1):
                        output_image = gr.Image(
                            type="pil", label="Sorted Image", height=400
                        )

                        status_text = gr.Textbox(
                            label="Status",
                            placeholder="Upload an image and click 'Sort Pixels' to begin...",
                            interactive=False,
                        )

                with gr.Row():
                    interval_dropdown = gr.Dropdown(
                        choices=interval_functions,
                        value="random",
                        label="Interval Function",
                        info="How to group pixels for sorting",
                    )
                    sorting_dropdown = gr.Dropdown(
                        choices=sorting_functions,
                        value="lightness",
                        label="Sorting Function",
                        info="How to sort pixels within each group",
                    )

                with gr.Row():
                    randomness_slider = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=10,
                        step=1,
                        label="Randomness %",
                        info="Percentage of intervals to leave unsorted",
                    )
                    angle_slider = gr.Slider(
                        minimum=0,
                        maximum=359,
                        value=0,
                        step=1,
                        label="Rotation Angle",
                        info="Rotate image before sorting (degrees)",
                        scale=3
                    )
                    angle_visualization = gr.Image(
                        label="Angle Preview",
                        type="pil",
                        height=120,
                        width=120,
                        interactive=False,
                        show_label=False,
                        container=False,
                        scale=1
                    )
                
                with gr.Row():
                    scale_slider = gr.Slider(
                        minimum=10,
                        maximum=100,
                        value=100,
                        step=5,
                        label="Image Scale %",
                        info="Scale down large images for more visible effects and faster processing"
                    )
                    scale_info = gr.Textbox(
                        label="Scaled Dimensions",
                        value="Upload an image to see dimensions",
                        interactive=False,
                        scale=1
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
                        info="Lower lightness threshold for interval detection",
                    )
                    upper_threshold_slider = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        value=0.8,
                        step=0.01,
                        label="Upper Threshold",
                        info="Upper lightness threshold for interval detection",
                    )
                
                threshold_visualization = gr.Image(
                    label="Threshold Preview",
                    type="pil",
                    height=80,
                    interactive=False,
                    show_label=False,
                    container=False
                )

                gr.Markdown("### Interval Parameters")
                characteristic_length_slider = gr.Slider(
                    minimum=1,
                    maximum=500,
                    value=50,
                    step=1,
                    label="Characteristic Length",
                    info="Base length for random and wave intervals",
                )

                gr.Markdown("### Cellular Automata Parameters")
                gr.Markdown(
                    "These parameters are used when 'file' or 'file-edges' interval functions are selected."
                )

                with gr.Row():
                    ca_rule_slider = gr.Slider(
                        minimum=-1,
                        maximum=255,
                        value=-1,
                        step=1,
                        label="CA Rule Number",
                        info="Cellular automata rule (0-255). Use -1 for random selection from recommended rules.",
                        scale=3,
                    )
                    ca_preview_button = gr.Button("🔍 Preview CA", size="sm", scale=1)

                ca_preview_image = gr.Image(
                    label="Cellular Automata Preview",
                    type="pil",
                    height=200,
                    visible=True,
                    interactive=False,
                )

                with gr.Accordion("Recommended CA Rules", open=False):
                    gr.Markdown(
                        """
                    **Recommended elementary cellular automata rules for interesting patterns:**
                    - **Rule 26, 19, 23, 25**: Simple patterns with structure
                    - **Rule 35, 106, 11**: More complex organized patterns  
                    - **Rule 110**: Turing complete, creates complex structures
                    - **Rule 45, 41, 105**: Irregular but structured patterns
                    - **Rule 54, 3, 15, 9**: Various geometric patterns
                    - **Rule 154, 142**: Dense, fractal-like patterns
                    
                    Set to -1 to randomly select from these recommended rules, or choose a specific number 0-255.
                    """
                    )

                # Function descriptions
                gr.Markdown("### Function Descriptions")

                with gr.Accordion("Interval Functions", open=False):
                    gr.Markdown(
                        """
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
                    """
                    )

                with gr.Accordion("Sorting Functions", open=False):
                    gr.Markdown(
                        """
                    - **lightness**: Sort by HSV lightness value
                    - **intensity**: Sort by sum of RGB values
                    - **hue**: Sort by HSV hue value
                    - **saturation**: Sort by HSV saturation value
                    - **red/green/blue**: Sort by individual color channels
                    - **minimum/maximum**: Sort by min/max RGB values
                    """
                    )

            # Processing button
            process_button = gr.Button("Sort Pixels", variant="primary", size="lg")

            # Set up the CA preview function
            ca_preview_button.click(
                fn=self.preview_cellular_automata,
                inputs=[ca_rule_slider],
                outputs=[ca_preview_image],
                show_progress=False,
            )

            # Set up the angle visualization (updates in real-time as slider moves)
            angle_slider.change(
                fn=self.create_angle_visualization,
                inputs=[angle_slider],
                outputs=[angle_visualization],
                show_progress=False,
            )

            # Initialize angle visualization with default value
            interface.load(
                fn=self.create_angle_visualization,
                inputs=[angle_slider],
                outputs=[angle_visualization],
            )
            
            # Set up the threshold visualization (updates in real-time as sliders move)
            bottom_threshold_slider.change(
                fn=self.create_threshold_visualization,
                inputs=[bottom_threshold_slider, upper_threshold_slider],
                outputs=[threshold_visualization],
                show_progress=False,
            )
            
            upper_threshold_slider.change(
                fn=self.create_threshold_visualization,
                inputs=[bottom_threshold_slider, upper_threshold_slider],
                outputs=[threshold_visualization],
                show_progress=False,
            )
            
            # Initialize threshold visualization with default values
            interface.load(
                fn=self.create_threshold_visualization,
                inputs=[bottom_threshold_slider, upper_threshold_slider],
                outputs=[threshold_visualization],
            )
            
            # Set up dimension display updates when image or scale changes
            input_image.change(
                fn=self.calculate_scaled_dimensions,
                inputs=[input_image, scale_slider],
                outputs=[scale_info],
                show_progress=False,
            )
            
            scale_slider.change(
                fn=self.calculate_scaled_dimensions,
                inputs=[input_image, scale_slider],
                outputs=[scale_info],
                show_progress=False,
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
                    ca_rule_slider,
                    scale_slider,
                ],
                outputs=[output_image, status_text],
                show_progress=True,
            )

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
