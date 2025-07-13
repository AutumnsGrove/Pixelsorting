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
from ..config.presets import (
    list_presets, get_preset, get_preset_descriptions, 
    create_custom_preset, register_preset
)
from ..effects.sorting_functions import get_sorting_function


class GradioInterface:
    """
    Gradio interface manager for the pixel sorting application.
    """

    def __init__(self):
        """Initialize the Gradio interface."""
        self.current_processor: Optional[PixelSorter] = None
        self.example_images = self._get_example_images()
        self.custom_presets_file = os.path.join(os.path.expanduser("~"), ".pixelsort_custom_presets.json")

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

    def load_custom_presets(self):
        """Load custom presets from file."""
        import json
        try:
            if os.path.exists(self.custom_presets_file):
                with open(self.custom_presets_file, 'r') as f:
                    custom_presets_data = json.load(f)
                    for preset_data in custom_presets_data:
                        from ..config.presets import Preset
                        preset = Preset.from_dict(preset_data)
                        register_preset(preset)
        except Exception as e:
            print(f"Error loading custom presets: {e}")

    def save_custom_presets(self):
        """Save custom presets to file."""
        import json
        try:
            # Get all presets and filter for custom ones (not built-in)
            all_preset_names = list_presets()
            built_in_presets = {'main', 'file', 'random', 'kims', 'gentle', 'intense', 'waves', 'edges'}
            
            custom_preset_data = []
            for preset_name in all_preset_names:
                if preset_name not in built_in_presets:
                    preset = get_preset(preset_name)
                    if preset:
                        custom_preset_data.append(preset.to_dict())
            
            with open(self.custom_presets_file, 'w') as f:
                json.dump(custom_preset_data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom presets: {e}")

    def load_preset_values(self, preset_name: str):
        """
        Load preset values and return them for updating GUI controls.
        
        Args:
            preset_name: Name of preset to load
            
        Returns:
            Tuple of values for GUI controls
        """
        if not preset_name or preset_name == "Select a preset...":
            return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), 
                   gr.update(), gr.update(), gr.update(), "")
        
        preset = get_preset(preset_name)
        if not preset:
            return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), 
                   gr.update(), gr.update(), gr.update(), f"❌ Preset '{preset_name}' not found")
        
        config = preset.sorting_config
        
        # Return values for all the GUI controls
        return (
            config.interval_function,           # interval_dropdown
            config.sorting_function,            # sorting_dropdown
            config.randomness,                  # randomness_slider
            config.angle,                       # angle_slider
            config.bottom_threshold,            # bottom_threshold_slider
            config.upper_threshold,             # upper_threshold_slider
            config.clength,                     # characteristic_length_slider
            config.ca_rule_number if config.ca_rule_number is not None else -1,  # ca_rule_slider
            f"✅ Loaded preset: {preset.name} - {preset.description}"  # status message
        )

    def save_current_as_preset(self, preset_name: str, interval_function: str, sorting_function: str, 
                             randomness: float, angle: float, bottom_threshold: float, 
                             upper_threshold: float, characteristic_length: int, ca_rule_number: int):
        """
        Save current settings as a new preset.
        
        Args:
            preset_name: Name for the new preset
            Other args: Current values from GUI controls
            
        Returns:
            Tuple of (updated preset choices, status message)
        """
        if not preset_name or preset_name.strip() == "":
            return gr.update(), "❌ Please enter a preset name"
        
        preset_name = preset_name.strip()
        
        # Check if preset already exists
        if get_preset(preset_name):
            return gr.update(), f"❌ Preset '{preset_name}' already exists"
        
        try:
            # Create custom preset
            custom_preset = create_custom_preset(
                name=preset_name,
                description=f"Custom preset: {preset_name}",
                bottom_threshold=bottom_threshold,
                upper_threshold=upper_threshold,
                clength=characteristic_length,
                randomness=randomness,
                angle=angle,
                interval_function=interval_function,
                sorting_function=sorting_function,
                ca_rule_number=ca_rule_number if ca_rule_number != -1 else None
            )
            
            # Register the preset
            register_preset(custom_preset)
            
            # Save to file
            self.save_custom_presets()
            
            # Update dropdown choices
            preset_choices = ["Select a preset..."] + list_presets()
            
            return gr.update(choices=preset_choices), f"✅ Saved preset: {preset_name}"
            
        except Exception as e:
            return gr.update(), f"❌ Error saving preset: {str(e)}"

    def create_sorting_function_visualization(self, sorting_function: str) -> Image.Image:
        """
        Create a visual representation of how a sorting function orders pixels.
        
        Args:
            sorting_function: Name of the sorting function
            
        Returns:
            PIL Image showing before/after comparison of sorted pixels
        """
        try:
            # Create a sample of diverse colors to show how they get sorted
            width = 400
            height = 100
            strip_height = 30
            
            # Generate sample pixels with diverse properties
            sample_pixels = []
            num_samples = 40
            
            # Create a variety of interesting colors
            import colorsys
            for i in range(num_samples):
                if i < 8:
                    # Pure colors across hue spectrum
                    hue = i / 8.0
                    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    pixel = (int(r * 255), int(g * 255), int(b * 255), 255)
                elif i < 16:
                    # Grayscale gradient
                    gray = int((i - 8) * 255 / 7)
                    pixel = (gray, gray, gray, 255)
                elif i < 24:
                    # Saturated to desaturated reds
                    sat = 1.0 - (i - 16) / 8.0
                    r, g, b = colorsys.hsv_to_rgb(0.0, sat, 1.0)
                    pixel = (int(r * 255), int(g * 255), int(b * 255), 255)
                elif i < 32:
                    # Dark to light blues
                    value = (i - 24) / 8.0
                    r, g, b = colorsys.hsv_to_rgb(0.6, 1.0, value)
                    pixel = (int(r * 255), int(g * 255), int(b * 255), 255)
                else:
                    # Random mix
                    import random
                    pixel = (
                        random.randint(0, 255),
                        random.randint(0, 255), 
                        random.randint(0, 255),
                        255
                    )
                sample_pixels.append(pixel)
            
            # Get the sorting function
            sort_func = get_sorting_function(sorting_function)
            
            # Create the visualization image
            img = Image.new("RGB", (width, height), color=(250, 250, 250))
            
            # Calculate pixel width
            pixel_width = width // len(sample_pixels)
            
            # Draw original (unsorted) pixels in top strip
            for i, pixel in enumerate(sample_pixels):
                x_start = i * pixel_width
                x_end = min((i + 1) * pixel_width, width)
                
                # Draw pixel color
                for x in range(x_start, x_end):
                    for y in range(5, 5 + strip_height):
                        img.putpixel((x, y), pixel[:3])
            
            # Sort the pixels using the selected function
            sorted_pixels = sorted(sample_pixels, key=sort_func)
            
            # Draw sorted pixels in bottom strip
            for i, pixel in enumerate(sorted_pixels):
                x_start = i * pixel_width
                x_end = min((i + 1) * pixel_width, width)
                
                # Draw pixel color
                for x in range(x_start, x_end):
                    for y in range(height - strip_height - 5, height - 5):
                        img.putpixel((x, y), pixel[:3])
            
            # Add labels and border
            draw = ImageDraw.Draw(img)
            
            # Draw borders around strips
            draw.rectangle([0, 4, width-1, 5 + strip_height], outline=(100, 100, 100), width=1)
            draw.rectangle([0, height - strip_height - 6, width-1, height - 4], outline=(100, 100, 100), width=1)
            
            # Add text labels
            draw.text((5, 1), "Original", fill=(50, 50, 50))
            draw.text((5, height - strip_height - 20), f"Sorted by: {sorting_function}", fill=(50, 50, 50))
            
            # Add explanation of what this function does
            function_explanations = {
                "lightness": "Dark → Light (HSV Value)",
                "intensity": "Low → High (Sum of RGB)",
                "hue": "Red → Yellow → Green → Blue → Purple",
                "saturation": "Dull/Gray → Vivid/Colorful",
                "red": "Low Red → High Red",
                "green": "Low Green → High Green", 
                "blue": "Low Blue → High Blue",
                "minimum": "Dark shadows → Bright highlights",
                "maximum": "Muted → Intense colors"
            }
            
            explanation = function_explanations.get(sorting_function, "Custom sorting")
            text_bbox = draw.textbbox((0, 0), explanation)
            text_width = text_bbox[2] - text_bbox[0]
            draw.text((width - text_width - 5, height - 15), explanation, fill=(80, 80, 80))
            
            return img
            
        except Exception as e:
            print(f"Error creating sorting function visualization: {e}")
            # Return a simple placeholder
            placeholder = Image.new("RGB", (400, 100), color=(200, 200, 200))
            draw = ImageDraw.Draw(placeholder)
            draw.text((10, 40), f"Preview not available for: {sorting_function}", fill=(100, 100, 100))
            return placeholder

    def create_threshold_overlay(self, image: Image.Image, bottom_threshold: float, upper_threshold: float, overlay_enabled: bool = True) -> Image.Image:
        """
        Create a live overlay showing which pixels would be affected by threshold settings.
        
        Args:
            image: Input PIL Image
            bottom_threshold: Lower threshold value (0.0-1.0)
            upper_threshold: Upper threshold value (0.0-1.0)
            overlay_enabled: Whether to show the overlay
            
        Returns:
            PIL Image with threshold overlay (like focus peaking on cameras)
        """
        if image is None:
            # Return a placeholder when no image is uploaded
            placeholder = Image.new("RGB", (400, 300), color=(240, 240, 240))
            draw = ImageDraw.Draw(placeholder)
            draw.text((120, 140), "Upload an image to see threshold preview", fill=(100, 100, 100))
            return placeholder
        
        if not overlay_enabled:
            return image
        
        try:
            # Convert image to RGB if needed
            if image.mode != "RGB":
                display_image = image.convert("RGB")
            else:
                display_image = image.copy()
            
            # Resize if image is too large for preview (for performance)
            max_preview_size = 800
            if max(display_image.size) > max_preview_size:
                aspect_ratio = display_image.size[0] / display_image.size[1]
                if display_image.size[0] > display_image.size[1]:
                    new_size = (max_preview_size, int(max_preview_size / aspect_ratio))
                else:
                    new_size = (int(max_preview_size * aspect_ratio), max_preview_size)
                display_image = display_image.resize(new_size, Image.LANCZOS)
            
            # Convert to array for faster processing
            import numpy as np
            img_array = np.array(display_image)
            
            # Calculate lightness for each pixel (same method as in pixel sorting)
            # Using RGB to HSV conversion for lightness calculation
            def rgb_to_lightness(r, g, b):
                """Convert RGB to lightness (HSV Value)"""
                r, g, b = r / 255.0, g / 255.0, b / 255.0
                return max(r, g, b)  # HSV Value component
            
            # Create lightness map
            height, width = img_array.shape[:2]
            lightness_map = np.zeros((height, width))
            
            for y in range(height):
                for x in range(width):
                    r, g, b = img_array[y, x]
                    lightness_map[y, x] = rgb_to_lightness(r, g, b)
            
            # Create overlay mask for pixels that would be sorted
            overlay_array = img_array.copy().astype(np.float32)
            
            # Pixels below bottom threshold (will be sorted) - red overlay
            below_mask = lightness_map < bottom_threshold
            if np.any(below_mask):
                overlay_array[below_mask, 0] = np.minimum(255, overlay_array[below_mask, 0] + 100)  # More red
                overlay_array[below_mask, 1] = np.maximum(0, overlay_array[below_mask, 1] - 30)     # Less green
                overlay_array[below_mask, 2] = np.maximum(0, overlay_array[below_mask, 2] - 30)     # Less blue
            
            # Pixels above upper threshold (will be sorted) - blue overlay  
            above_mask = lightness_map > upper_threshold
            if np.any(above_mask):
                overlay_array[above_mask, 0] = np.maximum(0, overlay_array[above_mask, 0] - 30)     # Less red
                overlay_array[above_mask, 1] = np.maximum(0, overlay_array[above_mask, 1] - 30)     # Less green
                overlay_array[above_mask, 2] = np.minimum(255, overlay_array[above_mask, 2] + 100)  # More blue
            
            # Create zebra-like striping for better visibility (like DSLR focus peaking)
            stripe_mask = (np.arange(height)[:, None] + np.arange(width)[None, :]) % 4 < 2
            
            # Apply stronger overlay on stripe areas
            strong_below = below_mask & stripe_mask
            strong_above = above_mask & stripe_mask
            
            if np.any(strong_below):
                overlay_array[strong_below, 0] = np.minimum(255, overlay_array[strong_below, 0] + 50)
                overlay_array[strong_below, 1] = np.maximum(0, overlay_array[strong_below, 1] - 50)
                overlay_array[strong_below, 2] = np.maximum(0, overlay_array[strong_below, 2] - 50)
            
            if np.any(strong_above):
                overlay_array[strong_above, 0] = np.maximum(0, overlay_array[strong_above, 0] - 50)
                overlay_array[strong_above, 1] = np.maximum(0, overlay_array[strong_above, 1] - 50)
                overlay_array[strong_above, 2] = np.minimum(255, overlay_array[strong_above, 2] + 50)
            
            # Convert back to image
            overlay_array = np.clip(overlay_array, 0, 255).astype(np.uint8)
            result_image = Image.fromarray(overlay_array)
            
            # Add small legend/info overlay
            draw = ImageDraw.Draw(result_image)
            
            # Add legend text with background rectangles for visibility
            legend_x = result_image.width - 210
            legend_y = 10
            
            # Draw background rectangles for text visibility
            draw.rectangle([legend_x, legend_y, result_image.width - 10, legend_y + 50], fill=(0, 0, 0, 180), outline=(255, 255, 255))
            
            # Add legend text
            draw.text((legend_x + 5, legend_y + 5), "Threshold Preview:", fill=(255, 255, 255))
            draw.text((legend_x + 5, legend_y + 20), f"Red: Below {bottom_threshold:.2f}", fill=(255, 100, 100))
            draw.text((legend_x + 5, legend_y + 35), f"Blue: Above {upper_threshold:.2f}", fill=(100, 100, 255))
            
            return result_image
            
        except Exception as e:
            print(f"Error creating threshold overlay: {e}")
            # Return original image if overlay creation fails
            return image if image else Image.new("RGB", (400, 300), color=(200, 200, 200))

    def create_interface(self) -> gr.Blocks:
        """
        Create and return the Gradio interface.

        Returns:
            Configured Gradio Blocks interface
        """
        # Load custom presets on interface creation
        self.load_custom_presets()
        
        # Get available functions
        interval_functions = list_interval_functions()
        sorting_functions = list_sorting_functions()
        
        # Get available presets
        preset_names = ["Select a preset..."] + list_presets()
        preset_descriptions = get_preset_descriptions()

        with gr.Blocks(
            title="Pixel Sorter",
            theme=gr.themes.Origin(),
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

                # Processing button - moved to top for easy access
                process_button = gr.Button("Sort Pixels", variant="primary", size="lg")

                with gr.Row():
                    interval_dropdown = gr.Dropdown(
                        choices=interval_functions,
                        value="random",
                        label="Interval Function",
                        info="How to group pixels for sorting",
                        scale=1
                    )
                    sorting_dropdown = gr.Dropdown(
                        choices=sorting_functions,
                        value="lightness",
                        label="Sorting Function",
                        info="How to sort pixels within each group",
                        scale=1
                    )
                
                # Add sorting function visualization
                sorting_visualization = gr.Image(
                    label="Sorting Preview",
                    type="pil",
                    height=120,
                    interactive=False,
                    show_label=True,
                    container=True
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
                
                # Add live threshold overlay on uploaded image
                gr.Markdown("### Live Threshold Overlay")
                gr.Markdown("See which pixels will be affected by your threshold settings (like focus peaking on cameras):")
                
                with gr.Row():
                    overlay_toggle = gr.Checkbox(
                        label="Enable Threshold Overlay",
                        value=True,
                        info="Show red/blue overlay on pixels that will be sorted",
                        scale=1
                    )
                
                threshold_overlay_image = gr.Image(
                    label="Threshold Overlay Preview",
                    type="pil",
                    height=300,
                    interactive=False,
                    show_label=True,
                    container=True
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

            with gr.Tab("Presets"):
                gr.Markdown("### Load Presets")
                gr.Markdown("Choose from built-in presets or your saved custom presets:")
                
                with gr.Row():
                    preset_dropdown = gr.Dropdown(
                        choices=preset_names,
                        value="Select a preset...",
                        label="Choose Preset",
                        info="Select a preset to load its settings",
                        scale=2
                    )
                    load_preset_button = gr.Button("Load Preset", variant="secondary", scale=1)
                
                # Status for preset loading
                preset_status = gr.Textbox(
                    label="Preset Status",
                    value="",
                    interactive=False,
                    container=False
                )
                
                # Display preset descriptions
                with gr.Accordion("Preset Descriptions", open=False):
                    descriptions_text = "\n".join([f"**{name}**: {desc}" for name, desc in preset_descriptions.items()])
                    gr.Markdown(descriptions_text)
                
                gr.Markdown("---")
                gr.Markdown("### Save Current Settings as Preset")
                gr.Markdown("Save your current advanced settings configuration as a new preset:")
                
                with gr.Row():
                    new_preset_name = gr.Textbox(
                        label="Preset Name",
                        placeholder="Enter a name for your custom preset...",
                        scale=2
                    )
                    save_preset_button = gr.Button("💾 Save Preset", variant="primary", scale=1)
                
                save_preset_status = gr.Textbox(
                    label="Save Status",
                    value="",
                    interactive=False,
                    container=False
                )

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
            
            # Set up the sorting function visualization (updates in real-time as dropdown changes)
            sorting_dropdown.change(
                fn=self.create_sorting_function_visualization,
                inputs=[sorting_dropdown],
                outputs=[sorting_visualization],
                show_progress=False,
            )
            
            # Initialize sorting function visualization with default value
            interface.load(
                fn=self.create_sorting_function_visualization,
                inputs=[sorting_dropdown],
                outputs=[sorting_visualization],
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
            
            # Set up the threshold overlay (updates when sliders change or image changes)
            bottom_threshold_slider.change(
                fn=self.create_threshold_overlay,
                inputs=[input_image, bottom_threshold_slider, upper_threshold_slider, overlay_toggle],
                outputs=[threshold_overlay_image],
                show_progress=False,
            )
            
            upper_threshold_slider.change(
                fn=self.create_threshold_overlay,
                inputs=[input_image, bottom_threshold_slider, upper_threshold_slider, overlay_toggle],
                outputs=[threshold_overlay_image],
                show_progress=False,
            )
            
            overlay_toggle.change(
                fn=self.create_threshold_overlay,
                inputs=[input_image, bottom_threshold_slider, upper_threshold_slider, overlay_toggle],
                outputs=[threshold_overlay_image],
                show_progress=False,
            )
            
            # Update overlay when input image changes
            input_image.change(
                fn=self.create_threshold_overlay,
                inputs=[input_image, bottom_threshold_slider, upper_threshold_slider, overlay_toggle],
                outputs=[threshold_overlay_image],
                show_progress=False,
            )
            
            # Initialize threshold overlay with default values
            interface.load(
                fn=self.create_threshold_overlay,
                inputs=[input_image, bottom_threshold_slider, upper_threshold_slider, overlay_toggle],
                outputs=[threshold_overlay_image],
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
            
            # Set up preset loading functionality
            load_preset_button.click(
                fn=self.load_preset_values,
                inputs=[preset_dropdown],
                outputs=[
                    interval_dropdown,
                    sorting_dropdown,
                    randomness_slider,
                    angle_slider,
                    bottom_threshold_slider,
                    upper_threshold_slider,
                    characteristic_length_slider,
                    ca_rule_slider,
                    preset_status
                ],
                show_progress=False,
            )
            
            # Set up preset saving functionality
            save_preset_button.click(
                fn=self.save_current_as_preset,
                inputs=[
                    new_preset_name,
                    interval_dropdown,
                    sorting_dropdown,
                    randomness_slider,
                    angle_slider,
                    bottom_threshold_slider,
                    upper_threshold_slider,
                    characteristic_length_slider,
                    ca_rule_slider
                ],
                outputs=[preset_dropdown, save_preset_status],
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
