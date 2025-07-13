"""
Interval functions for pixel sorting operations.

This module contains functions that determine how pixels are grouped
into intervals for sorting.
"""

from typing import List, Dict, Callable
import random as rand
from PIL import Image, ImageFilter
from tqdm import tqdm, trange
from numpy import array, mgrid
from numpy.random import choice, shuffle

from ..utils.image_utils import (
    open_image, 
    image_to_pixel_array, 
    append_pixel_from_image,
    apply_edge_filter
)
from .special_effects import (
    generate_elementary_cellular_automata,
    apply_thanos_snap,
    shuffle_image_rows,
    shuffle_image_vertically
)


# Type aliases
PixelArray = List[List[tuple]]  # 3D array of pixels
IntervalArray = List[List[int]]  # 2D array of interval boundaries
IntervalFunction = Callable[[PixelArray, dict], IntervalArray]


# Constants for black and white pixels
BLACK_PIXEL = (0, 0, 0, 255)
WHITE_PIXEL = (255, 255, 255, 255)


def random_width(characteristic_length: float) -> float:
    """
    Generate a random width based on characteristic length.
    
    Args:
        characteristic_length: Base length for randomization
        
    Returns:
        Random width value
    """
    return characteristic_length * (1 - rand.random())


def append_black_white_pixel(pixel_list: List[List[tuple]], x: int, y: int, 
                            data: PixelArray, threshold: float) -> None:
    """
    Append either black or white pixel based on lightness threshold.
    
    Args:
        pixel_list: List to append to
        x: X coordinate
        y: Y coordinate
        data: Pixel data array
        threshold: Lightness threshold
    """
    from .sorting_functions import lightness_sort
    
    if lightness_sort(data[y][x]) < threshold:
        pixel_list[y].append(WHITE_PIXEL)
    else:
        pixel_list[y].append(BLACK_PIXEL)


def random_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate random intervals for pixel sorting.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing 'clength' parameter
        
    Returns:
        2D array of interval boundaries
    """
    intervals = []
    
    for y in trange(len(pixels), desc="Determining intervals...".ljust(30)):
        intervals.append([])
        x = 0
        while True:
            width = random_width(args["clength"])
            x += width
            if x > len(pixels[0]):
                intervals[y].append(len(pixels[0]))
                break
            else:
                intervals[y].append(int(x))
    
    return intervals


def threshold_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate intervals based on lightness thresholds.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing 'bottom_threshold' and 'upper_threshold'
        
    Returns:
        2D array of interval boundaries
    """
    from .sorting_functions import lightness_sort
    
    intervals = []
    
    for y in trange(len(pixels), desc="Determining intervals...".ljust(30)):
        intervals.append([])
        for x in range(len(pixels[0])):
            pixel_lightness = lightness_sort(pixels[y][x])
            if (pixel_lightness < args["bottom_threshold"] or 
                pixel_lightness > args["upper_threshold"]):
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    
    return intervals


def edge_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate intervals based on edge detection.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing image parameters
        
    Returns:
        2D array of interval boundaries
    """
    # Load and process edge data
    img = open_image(args["url"], args["internet"])
    img = img.rotate(args["angle"], expand=True)
    edge_img = apply_edge_filter(img).convert("RGBA")
    edge_data = edge_img.load()
    
    filter_pixels = image_to_pixel_array(
        len(pixels[0]), len(pixels), edge_data, "Finding threshold..."
    )
    
    edge_pixels = []
    intervals = []
    
    # Create black/white edge map
    for y in trange(len(pixels), desc="Thresholding...".ljust(30)):
        edge_pixels.append([])
        for x in range(len(pixels[0])):
            append_black_white_pixel(edge_pixels, x, y, filter_pixels, args["bottom_threshold"])
    
    # Clean up edges
    for y in tqdm(range(len(pixels) - 1, 1, -1), desc="Cleaning up...".ljust(30)):
        for x in range(len(pixels[0]) - 1, 1, -1):
            if (edge_pixels[y][x] == BLACK_PIXEL and 
                edge_pixels[y][x - 1] == BLACK_PIXEL):
                edge_pixels[y][x] = WHITE_PIXEL
    
    # Define intervals
    for y in trange(len(pixels), desc="Defining intervals...".ljust(30)):
        intervals.append([])
        for x in range(len(pixels[0])):
            if edge_pixels[y][x] == BLACK_PIXEL:
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    
    return intervals


def wave_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate wave-like intervals with slight randomization.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing 'clength' parameter
        
    Returns:
        2D array of interval boundaries
    """
    intervals = []
    
    for y in trange(len(pixels), desc="Determining intervals...".ljust(30)):
        intervals.append([])
        x = 0
        while True:
            width = args["clength"] + rand.randint(0, 10)
            x += width
            if x > len(pixels[0]):
                intervals[y].append(len(pixels[0]))
                break
            else:
                intervals[y].append(x)
    
    return intervals


def no_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Create single intervals spanning entire rows (no sorting).
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary (unused)
        
    Returns:
        2D array with single interval per row
    """
    intervals = []
    for y in trange(len(pixels), desc="Determining intervals...".ljust(30)):
        intervals.append([len(pixels[y])])
    return intervals


def file_mask_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate intervals based on a cellular automata mask file.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing parameters including 'ca_rule_number'
        
    Returns:
        2D array of interval boundaries
    """
    # Generate cellular automata image
    rule_number = args.get('ca_rule_number', None)
    ca_img = generate_elementary_cellular_automata(
        len(pixels[0]), len(pixels), rule_number
    ).resize((len(pixels[0]), len(pixels)), Image.LANCZOS)
    
    data = ca_img.load()
    file_pixels = image_to_pixel_array(len(pixels[0]), len(pixels), data, "Defining edges...")
    intervals = []
    
    # Clean up edges
    for y in tqdm(range(len(pixels) - 1, 1, -1), desc="Cleaning up edges...".ljust(30)):
        for x in range(len(pixels[0]) - 1, 1, -1):
            if (file_pixels[y][x] == BLACK_PIXEL and 
                file_pixels[y][x - 1] == BLACK_PIXEL):
                file_pixels[y][x] = WHITE_PIXEL
    
    # Define intervals
    for y in trange(len(pixels), desc="Defining intervals...".ljust(30)):
        intervals.append([])
        for x in range(len(pixels[0])):
            if file_pixels[y][x] == BLACK_PIXEL:
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    
    return intervals


def file_edges_intervals(pixels: PixelArray, args: dict) -> IntervalArray:
    """
    Generate intervals based on edge detection of a cellular automata file.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing image parameters including 'ca_rule_number'
        
    Returns:
        2D array of interval boundaries
    """
    # Generate cellular automata image and apply edge detection
    rule_number = args.get('ca_rule_number', None)
    ca_img = generate_elementary_cellular_automata(len(pixels[0]), len(pixels), rule_number)
    
    edge_img = (ca_img
                .rotate(args.get("angle", 0), expand=True)
                .resize((len(pixels[0]), len(pixels)), Image.LANCZOS)
                .filter(ImageFilter.FIND_EDGES)
                .convert("RGBA"))
    
    edge_data = edge_img.load()
    filter_pixels = image_to_pixel_array(
        len(pixels[0]), len(pixels), edge_data, "Defining edges..."
    )
    
    edge_pixels = []
    intervals = []
    
    # Create black/white edge map
    for y in trange(len(pixels), desc="Thresholding...".ljust(30)):
        edge_pixels.append([])
        for x in range(len(pixels[0])):
            append_black_white_pixel(edge_pixels, x, y, filter_pixels, 
                                   args.get("bottom_threshold", 0.25))
    
    # Clean up edges
    for y in tqdm(range(len(pixels) - 1, 1, -1), desc="Cleaning up edges...".ljust(30)):
        for x in range(len(pixels[0]) - 1, 1, -1):
            if (edge_pixels[y][x] == BLACK_PIXEL and 
                edge_pixels[y][x - 1] == BLACK_PIXEL):
                edge_pixels[y][x] = WHITE_PIXEL
    
    # Define intervals
    for y in trange(len(pixels), desc="Defining intervals...".ljust(30)):
        intervals.append([])
        for x in range(len(pixels[0])):
            if edge_pixels[y][x] == BLACK_PIXEL:
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    
    return intervals


def snap_intervals(pixels: PixelArray, args: dict) -> PixelArray:
    """
    Apply Thanos snap effect to the image and return modified pixels.
    
    Note: This is different from other interval functions as it returns
    modified pixels rather than intervals, representing a special effect.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary (unused for this function)
        
    Returns:
        3D array of pixels with snap effect applied
    """
    # Convert pixel array to PIL Image
    height = len(pixels)
    width = len(pixels[0]) if height > 0 else 0
    
    if height == 0 or width == 0:
        return pixels
    
    # Create image from pixels
    img = Image.new("RGBA", (width, height))
    for y in range(height):
        for x in range(width):
            if x < len(pixels[y]):
                img.putpixel((x, y), pixels[y][x])
    
    # Apply snap effect
    snapped_img = apply_thanos_snap(img)
    
    # Convert back to pixel array
    data = snapped_img.load()
    return image_to_pixel_array(width, height, data, "I hope they remember you...")


def shuffle_total_intervals(pixels: PixelArray, args: dict) -> PixelArray:
    """
    Apply row shuffling effect to the image and return modified pixels.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing 'url' and 'internet' for image loading
        
    Returns:
        3D array of pixels with shuffle effect applied
    """
    # Load original image and apply shuffle effect
    input_img = open_image(args["url"], args["internet"]).convert("RGBA")
    shuffled_img = shuffle_image_rows(input_img)
    
    # Convert to pixel array
    data = shuffled_img.load()
    size0, size1 = shuffled_img.size
    return image_to_pixel_array(size0, size1, data, "Recreating image...")


def shuffle_axis_intervals(pixels: PixelArray, args: dict) -> PixelArray:
    """
    Apply vertical shuffling effect to the image and return modified pixels.
    
    Args:
        pixels: 3D array of pixel values
        args: Dictionary containing 'url' and 'internet' for image loading
        
    Returns:
        3D array of pixels with shuffle effect applied
    """
    # Load original image and apply shuffle effect
    input_img = open_image(args["url"], args["internet"]).convert("RGBA")
    shuffled_img = shuffle_image_vertically(input_img)
    
    # Convert to pixel array
    data = shuffled_img.load()
    size0, size1 = shuffled_img.size
    return image_to_pixel_array(size0, size1, data, "Recreating image...")


# Registry of available interval functions
INTERVAL_FUNCTIONS: Dict[str, IntervalFunction] = {
    "random": random_intervals,
    "threshold": threshold_intervals,
    "edges": edge_intervals,
    "waves": wave_intervals,
    "none": no_intervals,
    "file": file_mask_intervals,
    "file-edges": file_edges_intervals,
    "snap": snap_intervals,
    "shuffle-total": shuffle_total_intervals,
    "shuffle-axis": shuffle_axis_intervals,
}


def get_interval_function(name: str) -> IntervalFunction:
    """
    Get an interval function by name.
    
    Args:
        name: Name of the interval function
        
    Returns:
        Interval function
        
    Raises:
        FunctionNotFoundError: If the interval function name is not found
    """
    if name not in INTERVAL_FUNCTIONS:
        from ..utils.exceptions import raise_function_not_found
        raise_function_not_found("interval", name, list(INTERVAL_FUNCTIONS.keys()))
    
    return INTERVAL_FUNCTIONS[name]


def list_interval_functions() -> List[str]:
    """
    Get a list of available interval function names.
    
    Returns:
        List of interval function names
    """
    return list(INTERVAL_FUNCTIONS.keys())