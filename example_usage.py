"""
Example usage of the refactored pixelsort modules.

This script demonstrates how to use the extracted and refactored components
from the pixelsort package.
"""

from PIL import Image
from pixelsort.utils.image_utils import open_image, image_to_pixel_array, set_pixel
from pixelsort.utils.config import SortingConfig, validate_config
from pixelsort.effects.sorting_functions import get_sorting_function, list_sorting_functions
from pixelsort.effects.interval_functions import get_interval_function, list_interval_functions
from pixelsort.core.sorting import apply_pixel_sort


def main():
    """
    Example of using the refactored pixelsort modules.
    """
    # Create configuration
    config = SortingConfig(
        bottom_threshold=0.25,
        upper_threshold=0.8,
        clength=50,
        randomness=10.0,
        angle=0.0,
        interval_function="random",
        sorting_function="lightness",
        url="images/default.jpg",
        internet=False
    )
    
    # Validate configuration
    try:
        validate_config(config)
        print("Configuration is valid!")
    except ValueError as e:
        print(f"Configuration error: {e}")
        return
    
    # List available functions
    print("Available sorting functions:", list_sorting_functions())
    print("Available interval functions:", list_interval_functions())
    
    # Load image
    try:
        image = open_image(config.url, config.internet)
        print(f"Loaded image: {image.size}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    # Convert to pixel array
    pixel_data = image.load()
    pixels = image_to_pixel_array(image.size[0], image.size[1], pixel_data, "Loading pixels")
    
    # Get functions
    try:
        interval_func = get_interval_function(config.interval_function)
        sorting_func = get_sorting_function(config.sorting_function)
    except KeyError as e:
        print(f"Function error: {e}")
        return
    
    # Apply pixel sorting
    print("Applying pixel sorting...")
    sorted_pixels = apply_pixel_sort(pixels, interval_func, sorting_func, config.to_dict())
    
    # Create output image
    output_image = Image.new("RGBA", image.size)
    for y in range(len(sorted_pixels)):
        for x in range(len(sorted_pixels[y])):
            if x < image.size[0] and y < image.size[1]:
                set_pixel(output_image, x, y, sorted_pixels)
    
    # Save result
    output_path = "output/example_sorted.png"
    output_image.save(output_path)
    print(f"Saved sorted image to: {output_path}")


if __name__ == "__main__":
    main()