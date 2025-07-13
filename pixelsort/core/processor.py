"""
Main pixel sorting processor.

This module contains the PixelSorter class that orchestrates the entire
pixel sorting process by coordinating image preparation, interval generation,
pixel sorting, and image reconstruction.
"""

from typing import Dict, Any, Optional
from PIL import Image
from tqdm import trange

from ..utils.image_utils import open_image, image_to_pixel_array
from ..utils.exceptions import ProcessingError, handle_processing_error
from ..effects.interval_functions import IntervalFunction, get_interval_function
from ..effects.sorting_functions import SortingFunction, get_sorting_function
from .sorting import sort_image, PixelArray


class PixelSorter:
    """
    Main pixel sorting processor that orchestrates the entire sorting pipeline.
    
    This class breaks down the pixel sorting process into clear steps:
    1. prepare_image() - Load, rotate, and convert image to pixel array
    2. generate_intervals() - Generate sorting intervals using interval function  
    3. sort_pixels() - Sort pixels within intervals using sorting function
    4. reconstruct_image() - Convert sorted pixels back to PIL Image
    """
    
    def __init__(self, interval_function: str, sorting_function: str, **kwargs):
        """
        Initialize the PixelSorter.
        
        Args:
            interval_function: Name of the interval function to use
            sorting_function: Name of the sorting function to use
            **kwargs: Additional arguments for the functions
        """
        self.interval_func = get_interval_function(interval_function)
        self.sorting_func = get_sorting_function(sorting_function)
        self.args = kwargs
        
        # Store intermediate results
        self.original_image: Optional[Image.Image] = None
        self.prepared_image: Optional[Image.Image] = None
        self.pixels: Optional[PixelArray] = None
        self.intervals: Optional[list] = None
        self.sorted_pixels: Optional[PixelArray] = None
        self.output_image: Optional[Image.Image] = None
    
    @handle_processing_error("image_preparation")
    def prepare_image(self, image_path_or_url: str, internet: bool = True) -> Image.Image:
        """
        Prepare the image for processing: load, rotate, and convert to pixel array.
        
        Args:
            image_path_or_url: Path to local image or URL to remote image
            internet: Whether internet is available for remote images
            
        Returns:
            Prepared PIL Image
        """
        # Load the image
        self.original_image = open_image(image_path_or_url, internet)
        
        # Rotate if angle is specified
        angle = self.args.get("angle", 0)
        if angle != 0:
            self.prepared_image = self.original_image.rotate(angle, expand=True)
        else:
            self.prepared_image = self.original_image
        
        # Convert to pixel array
        data = self.prepared_image.load()
        size0, size1 = self.prepared_image.size
        self.pixels = image_to_pixel_array(size0, size1, data, "Getting pixels...")
        
        return self.prepared_image
    
    @handle_processing_error("interval_generation") 
    def generate_intervals(self) -> list:
        """
        Generate sorting intervals using the configured interval function.
        
        Returns:
            2D array of interval boundaries or modified pixels for special effects
            
        Raises:
            ValueError: If image hasn't been prepared yet
        """
        if self.pixels is None:
            raise ValueError("Image must be prepared before generating intervals")
        
        # Add image URL and internet status to args for interval functions that need them
        args_with_image = self.args.copy()
        if hasattr(self, 'original_image') and self.original_image:
            # For interval functions that need to reload the image
            args_with_image['url'] = getattr(self, '_image_path', '')
            args_with_image['internet'] = getattr(self, '_internet', True)
        
        result = self.interval_func(self.pixels, args_with_image)
        
        # Check if this is a special effect that returns pixels instead of intervals
        interval_func_name = getattr(self.interval_func, '__name__', '')
        if interval_func_name in ['snap_intervals', 'shuffle_total_intervals', 'shuffle_axis_intervals']:
            # For special effects, the result is modified pixels, not intervals
            self.sorted_pixels = result
            self.intervals = None  # No intervals needed for special effects
            return None
        else:
            # Normal interval function
            self.intervals = result
            return self.intervals
    
    @handle_processing_error("pixel_sorting")
    def sort_pixels(self) -> PixelArray:
        """
        Sort pixels within intervals using the configured sorting function.
        
        Returns:
            3D array of sorted pixels
            
        Raises:
            ValueError: If intervals haven't been generated yet (unless special effect already applied)
        """
        if self.pixels is None:
            raise ValueError("Image must be prepared before sorting")
        
        # Check if special effects have already been applied
        if self.sorted_pixels is not None and self.intervals is None:
            # Special effect has already been applied, no additional sorting needed
            return self.sorted_pixels
        
        if self.intervals is None:
            raise ValueError("Intervals must be generated before sorting")
        
        self.sorted_pixels = sort_image(self.pixels, self.intervals, self.args, self.sorting_func)
        return self.sorted_pixels
    
    @handle_processing_error("image_reconstruction")
    def reconstruct_image(self) -> Image.Image:
        """
        Convert sorted pixels back to a PIL Image.
        
        Returns:
            PIL Image with sorted pixels
            
        Raises:
            ValueError: If pixels haven't been sorted yet
        """
        if self.sorted_pixels is None or self.prepared_image is None:
            raise ValueError("Pixels must be sorted before reconstructing image")
        
        # Create output image
        self.output_image = Image.new("RGBA", self.prepared_image.size)
        size0, size1 = self.output_image.size
        
        # Place sorted pixels
        for y in trange(size1, desc="Building output image...".ljust(30)):
            for x in range(size0):
                if (y < len(self.sorted_pixels) and 
                    x < len(self.sorted_pixels[y])):
                    self.output_image.putpixel((x, y), self.sorted_pixels[y][x])
        
        # Rotate back to original orientation if needed
        angle = self.args.get("angle", 0)
        if angle != 0:
            # Store the target size (should match original image dimensions)
            target_size = self.original_image.size if self.original_image else self.output_image.size
            
            # Rotate back (reverse the rotation)
            self.output_image = self.output_image.rotate(360 - angle, expand=True)
            
            # Crop to target size to remove extra space from rotation
            if self.output_image.size != target_size:
                # Calculate center crop coordinates
                img_width, img_height = self.output_image.size
                target_width, target_height = target_size
                
                # Only crop if the rotated image is larger than target
                if img_width >= target_width and img_height >= target_height:
                    left = (img_width - target_width) // 2
                    top = (img_height - target_height) // 2
                    right = left + target_width
                    bottom = top + target_height
                    
                    self.output_image = self.output_image.crop((left, top, right, bottom))
                else:
                    # If rotated image is smaller, resize to target
                    self.output_image = self.output_image.resize(target_size, Image.LANCZOS)
        
        return self.output_image
    
    def process_image(self, image_path_or_url: str, internet: bool = True) -> Image.Image:
        """
        Complete pixel sorting pipeline in one call.
        
        Args:
            image_path_or_url: Path to local image or URL to remote image
            internet: Whether internet is available for remote images
            
        Returns:
            PIL Image with sorted pixels
        """
        # Store for interval functions that might need to reload the image
        self._image_path = image_path_or_url
        self._internet = internet
        
        # Execute the full pipeline
        self.prepare_image(image_path_or_url, internet)
        self.generate_intervals()
        self.sort_pixels()
        return self.reconstruct_image()
    
    def save_result(self, output_path: str) -> None:
        """
        Save the processed image to a file.
        
        Args:
            output_path: Path where to save the output image
            
        Raises:
            ValueError: If no processed image is available
        """
        if self.output_image is None:
            raise ValueError("No processed image available to save")
        
        self.output_image.save(output_path)
    
    def get_processing_info(self) -> Dict[str, Any]:
        """
        Get information about the current processing configuration and state.
        
        Returns:
            Dictionary with processing information
        """
        info = {
            "interval_function": self.interval_func.__name__ if self.interval_func else None,
            "sorting_function": self.sorting_func.__name__ if self.sorting_func else None,
            "arguments": self.args.copy(),
            "original_size": self.original_image.size if self.original_image else None,
            "prepared_size": self.prepared_image.size if self.prepared_image else None,
            "output_size": self.output_image.size if self.output_image else None,
            "has_pixels": self.pixels is not None,
            "has_intervals": self.intervals is not None,
            "has_sorted_pixels": self.sorted_pixels is not None,
            "has_output": self.output_image is not None,
        }
        return info


class PixelSortProcessor:
    """
    High-level processor that works with SortingConfig objects.
    
    This class provides a simplified interface that matches what integration tests expect.
    """
    
    def __init__(self):
        """Initialize the processor."""
        self._sorter = None
    
    def process_image(self, config) -> Image.Image:
        """
        Process an image using the provided configuration.
        
        Args:
            config: SortingConfig object or dict with configuration
            
        Returns:
            Processed PIL Image
        """
        # Handle both SortingConfig objects and dicts
        if hasattr(config, 'to_dict'):
            config_dict = config.to_dict()
        else:
            config_dict = config
        
        # Extract parameters
        interval_function = config_dict.get('int_function', config_dict.get('interval_function', 'random'))
        sorting_function = config_dict.get('sorting_function', 'lightness')
        image_url = config_dict.get('url', '')
        internet = config_dict.get('internet', True)
        
        # Create sorter with parameters
        sorter_args = {
            'clength': config_dict.get('clength', 50),
            'bottom_threshold': config_dict.get('bottom_threshold', 0.25),
            'upper_threshold': config_dict.get('upper_threshold', 0.8),
            'randomness': config_dict.get('randomness', 10.0),
            'angle': config_dict.get('angle', 0.0),
        }
        
        self._sorter = PixelSorter(interval_function, sorting_function, **sorter_args)
        
        # Process the image
        return self._sorter.process_image(image_url, internet)


def create_processor(interval_function: str = "random", 
                    sorting_function: str = "lightness",
                    **kwargs) -> PixelSorter:
    """
    Factory function to create a PixelSorter instance.
    
    Args:
        interval_function: Name of the interval function to use
        sorting_function: Name of the sorting function to use
        **kwargs: Additional arguments for the functions
        
    Returns:
        Configured PixelSorter instance
    """
    return PixelSorter(interval_function, sorting_function, **kwargs)