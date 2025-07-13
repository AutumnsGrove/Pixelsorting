"""
Image processing utilities for the pixel sorting application.

This module contains image processing methods extracted from the GradioInterface class
to provide a clean separation of concerns. The ImageProcessor class handles image
scaling, dimension calculations, and the main image processing workflow.
"""

import os
import tempfile
from typing import Optional, Tuple
import gradio as gr
from PIL import Image

from ..core.processor import PixelSorter
from ..utils.config import SortingConfig, validate_config
from .progress_manager import ProgressManager


class ImageProcessor:
    """
    Image processor for pixel sorting operations.
    
    This class handles image scaling, dimension calculations, and the main
    image processing workflow for the Gradio interface.
    """

    def __init__(self):
        """Initialize the image processor."""
        self.current_processor: Optional[PixelSorter] = None

    @staticmethod
    def calculate_scaled_dimensions(image: Image.Image, scale_percent: float) -> str:
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

    @staticmethod
    def scale_image(image: Image.Image, scale_percent: float) -> Image.Image:
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
            ca_rule_number: CA rule number for cellular automata interval functions
            scale_percent: Image scaling percentage (10-100)
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