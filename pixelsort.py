# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# Core imports for pixel sorting functionality
from colorsys import rgb_to_hsv
from os import path, remove
from typing import List, Tuple, Callable, Any, Dict

# Third-party imports
import random as rand
from numpy import array, mgrid
from numpy.random import choice, shuffle
from PIL import Image, ImageFilter
from tqdm import tqdm, trange


BlackPixel = (0, 0, 0, 255)
WhitePixel = (255, 255, 255, 255)

# SORTING PIXELS #
lightness = lambda p: rgb_to_hsv(p[0], p[1], p[2])[2] / 255.0
intensity = lambda p: p[0] + p[1] + p[2]
hue = lambda p: rgb_to_hsv(p[0], p[1], p[2])[0] / 255.0
saturation = lambda p: rgb_to_hsv(p[0], p[1], p[2])[1] / 255.0
minimum = lambda p: min(p[0], p[1], p[2])

# Utility functions
def remove_old_file(file_path: str) -> None:
    """Remove a file if it exists."""
    if path.exists(file_path):
        remove(file_path)

def get_progress_bar(count: int, description: str):
    """Get a progress bar for the given count and description."""
    return trange(count, desc=f"{description:30}")

def set_pixel(image: Image.Image, x: int, y: int, pixel_data: List[List[Tuple]], y_idx: int, x_idx: int) -> None:
    """Set a pixel in an image from pixel data."""
    image.putpixel((x, y), pixel_data[y_idx][x_idx])


# MISC FUNCTIONS #


def extract_pixels(height: int, width: int, pixel_data, message: str) -> List[List[Tuple]]:
    """Extract pixel values from a PIL image into a 2D array.
    
    Args:
        height: Image height
        width: Image width
        pixel_data: PixelAccess object from img.load()
        message: Message for the progress bar
        
    Returns:
        2D array of pixel values
    """
    pixels = []
    for y in get_progress_bar(height, message):
        row = []
        for x in range(width):
            row.append(pixel_data[x, y])
        pixels.append(row)
    return pixels


def elementary_ca(width: int, height: int) -> Image.Image:
    """
    Generate a simple cellular automata image.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        PIL Image object
    """
    # Use a simple rule for cellular automata
    rules = [26, 19, 23, 25, 35, 106, 11, 110, 45, 41, 105, 54, 3, 15, 9, 154, 142]
    rulenumber = rules[rand.randrange(0, len(rules))]
    
    # Define colors
    true_pixel = (255, 255, 255)
    false_pixel = (0, 0, 0)
    
    # Generate rule dictionary
    def generate_rule(rulenumber) -> dict:
        rule = {}
        for left in [False, True]:
            for middle in [False, True]:
                for right in [False, True]:
                    rule[(left, middle, right)] = rulenumber % 2 == 1
                    rulenumber //= 2
        return rule
    
    # Generate cellular automata
    def generate_ca(rule):
        ca = []
        # Initialize first row randomly
        ca.append([])
        for x in range(width):
            ca[0].append(bool(rand.getrandbits(1)))
        
        # Generate succeeding generations
        for y in range(1, height):
            ca.append([])
            ca[y].append(bool(rand.getrandbits(1)))  # Left edge
            for x in range(1, width - 1):
                ca[y].append(rule[(ca[y - 1][x - 1], ca[y - 1][x], ca[y - 1][x + 1])])
            ca[y].append(bool(rand.getrandbits(1)))  # Right edge
        return ca
    
    rule = generate_rule(rulenumber)
    ca = generate_ca(rule)
    
    # Create image
    new_img = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            pixel = true_pixel if ca[y][x] else false_pixel
            new_img.putpixel((x, y), pixel)
    
    return new_img




def check_file_exists(file_path: str) -> bool:
    """Check if a file exists at the given path.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if file exists, False otherwise
    """
    return path.exists(file_path)


def open_image(file_path: str) -> Image.Image:
    """Open an image file and convert to RGBA format.
    
    Args:
        file_path: Path to the image file
        
    Returns:
        PIL Image object in RGBA format
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
        OSError: If the image cannot be opened
    """
    if not check_file_exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")
    
    try:
        return Image.open(file_path).convert("RGBA")
    except OSError as e:
        raise OSError(f"Cannot open image file '{file_path}': {e}")


def crop_to_reference(image_to_crop: Image.Image, reference_path: str) -> Image.Image:
    """Crop image to the size of a reference image.
    
    Assumes the relevant image is located in the center and crops away
    equal sizes on both sides.
    
    Args:
        image_to_crop: Image to be cropped
        reference_path: Path to the reference image
        
    Returns:
        Cropped image
    """
    reference_image = open_image(reference_path)
    reference_size = reference_image.size
    current_size = image_to_crop.size
    
    dx = current_size[0] - reference_size[0]
    dy = current_size[1] - reference_size[1]
    
    left = dx // 2
    upper = dy // 2
    right = left + reference_size[0]
    lower = upper + reference_size[1]
    
    return image_to_crop.crop(box=(left, upper, right, lower))




# READING FUNCTIONS #
def get_image_path(input_path: str) -> str:
    """Get the final image path, handling default cases.
    
    Args:
        input_path: User input path (can be empty for default)
        
    Returns:
        Final path to the image file
    """
    if input_path in ["", " "]:
        return "images/default.jpg"
    return input_path


def get_interval_function(function_name: str) -> Callable:
    """Get the interval function by name.
    
    Args:
        function_name: Name of the interval function
        
    Returns:
        The corresponding interval function
    """
    functions = {
        "random": random,
        "threshold": threshold,
        "edges": edge,
        "waves": waves,
        "snap": snap_sort,
        "file": file_mask,
        "file-edges": file_edges,
        "shuffle-total": shuffle_total,
        "shuffle-axis": shuffled_axis,
        "none": none,
    }
    return functions.get(function_name, random)


def get_sorting_function(function_name: str) -> Callable:
    """Get the sorting function by name.
    
    Args:
        function_name: Name of the sorting function
        
    Returns:
        The corresponding sorting function
    """
    functions = {
        "lightness": lightness,
        "hue": hue,
        "intensity": intensity,
        "minimum": minimum,
        "saturation": saturation,
    }
    return functions.get(function_name, lightness)


def apply_preset(preset_name: str) -> Dict[str, Any]:
    """Apply a preset configuration.
    
    Args:
        preset_name: Name of the preset to apply
        
    Returns:
        Dictionary with preset configuration
    """
    presets = {
        "default": {
            "interval_function": "random", 
            "sorting_function": "lightness",
            "bottom_threshold": 0.25,
            "upper_threshold": 0.8,
            "clength": 50,
            "angle": 0,
            "randomness": 10
        },
        "waves": {
            "interval_function": "waves",
            "sorting_function": "intensity", 
            "clength": 75,
            "randomness": 15
        },
        "threshold": {
            "interval_function": "threshold",
            "sorting_function": "hue",
            "bottom_threshold": 0.2,
            "upper_threshold": 0.9,
            "randomness": 5
        }
    }
    
    if preset_name not in presets:
        print(f"[WARNING] Invalid preset name '{preset_name}', using default")
        preset_name = "default"
    
    return presets[preset_name]


# SORTER #
def sort_image(pixels, intervals, args, sorting_function):
    """
    Sort pixels within intervals using the specified sorting function.
    
    Args:
        pixels: 3D array of pixel values
        intervals: 2D array of interval boundaries
        args: Dictionary containing 'randomness' parameter
        sorting_function: Function to sort pixels by
        
    Returns:
        3D array of sorted pixels
    """
    sorted_pixels = []
    sort_interval = lambda lst, func: [] if lst == [] else sorted(lst, key=func)
    
    for y in get_progress_bar(len(pixels), "Sorting..."):
        row = []
        x_min = 0
        for x_max in intervals[y]:
            interval = []
            for x in range(int(x_min), int(x_max)):
                if x < len(pixels[y]):
                    interval.append(pixels[y][x])
            
            # Apply randomness
            randomness = args.get("randomness", 0)
            if rand.randint(0, 100) >= randomness:
                row += sort_interval(interval, sorting_function)
            else:
                row += interval
            x_min = x_max
        
        # Pad row to original width if needed
        while len(row) < len(pixels[y]):
            row.append(pixels[y][len(row)])
        
        sorted_pixels.append(row)
    
    return sorted_pixels


# INTERVALS #
def edge(pixels, args):
    """Generate intervals based on edge detection (simplified version)."""
    intervals = []
    # Simplified edge detection - just use threshold-based intervals for now
    for y in get_progress_bar(len(pixels), "Determining intervals..."):
        intervals.append([])
        for x in range(len(pixels[0])):
            if lightness(pixels[y][x]) < args.get("bottom_threshold", 0.25):
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    return intervals


def threshold(pixels, args):
    """Generate intervals based on lightness thresholds."""
    intervals = []

    for y in get_progress_bar(len(pixels), "Determining intervals..."):
        intervals.append([])
        for x in range(len(pixels[0])):
            pixel_lightness = lightness(pixels[y][x])
            if (pixel_lightness < args.get("bottom_threshold", 0.25) or 
                pixel_lightness > args.get("upper_threshold", 0.8)):
                intervals[y].append(x)
        intervals[y].append(len(pixels[0]))
    return intervals


def random(pixels, args):
    """Generate random intervals."""
    intervals = []
    
    def random_width(characteristic_length):
        return characteristic_length * (1 - rand.random())

    for y in get_progress_bar(len(pixels), "Determining intervals..."):
        intervals.append([])
        x = 0
        while True:
            width = random_width(args.get("clength", 50))
            x += width
            if x > len(pixels[0]):
                intervals[y].append(len(pixels[0]))
                break
            else:
                intervals[y].append(int(x))
    return intervals


def waves(pixels, args):
    """Generate wave-like intervals with slight randomization."""
    intervals = []

    for y in get_progress_bar(len(pixels), "Determining intervals..."):
        intervals.append([])
        x = 0
        while True:
            width = args.get("clength", 50) + rand.randint(0, 10)
            x += width
            if x > len(pixels[0]):
                intervals[y].append(len(pixels[0]))
                break
            else:
                intervals[y].append(x)
    return intervals


def file_mask(pixels, args):
    """Generate intervals based on a cellular automata mask file."""
    img = elementary_ca(len(pixels[0]), len(pixels)).resize(
        (len(pixels[0]), len(pixels)), Image.ANTIALIAS
    )
    data = img.load()
    
    # Convert image data to pixel array
    file_pixels = extract_pixels(len(pixels), len(pixels[0]), data, "Defining edges...")
    intervals = []

    # Clean up edges (simplified)
    for y in tqdm(range(len(pixels) - 1, 1, -1), desc="Cleaning up edges...".ljust(30)):
        for x in range(len(pixels[0]) - 1, 1, -1):
            if (y < len(file_pixels) and x < len(file_pixels[y]) and 
                x - 1 < len(file_pixels[y])):
                if (file_pixels[y][x] == BlackPixel and 
                    file_pixels[y][x - 1] == BlackPixel):
                    file_pixels[y][x] = WhitePixel

    # Define intervals
    for y in get_progress_bar(len(pixels), "Defining intervals..."):
        intervals.append([])
        for x in range(len(pixels[0])):
            if y < len(file_pixels) and x < len(file_pixels[y]):
                if file_pixels[y][x] == BlackPixel:
                    intervals[y].append(x)
        intervals[y].append(len(pixels[0]))

    return intervals


def file_edges(pixels, args):
    """Generate intervals based on edge detection of a cellular automata file."""
    # Simplified version using threshold
    return threshold(pixels, args)


def snap_sort(pixels, args):
    """Apply Thanos snap effect (simplified version)."""
    print("The hardest choices require the strongest wills...")
    
    # Create a copy of pixels to modify
    pixels_snap = [row[:] for row in pixels]
    
    # Snap half the pixels randomly
    total_pixels = len(pixels) * len(pixels[0]) if pixels else 0
    snap_count = total_pixels // 2
    
    print(f'Number of those worthy of the sacrifice: {snap_count:,}')
    
    snapped = 0
    for y in range(len(pixels_snap)):
        for x in range(len(pixels_snap[y])):
            if snapped < snap_count and rand.random() < 0.5:
                pixels_snap[y][x] = (0, 0, 0, 0)
                snapped += 1
    
    print("Perfectly balanced, as all things should be.")
    return pixels_snap


def shuffle_total(pixels, args):
    """Apply row shuffling effect."""
    print("Creating array from image...")
    input_img = open_image(args["url"]).convert("RGBA")
    height = input_img.size[1]
    shuffled = array(input_img)

    for i in get_progress_bar(int(height), "Shuffling image..."):
        shuffle(shuffled[i])
    
    print("Saving shuffled image...")
    shuffled_img = Image.fromarray(shuffled, "RGBA")
    data = shuffled_img.load()

    size0, size1 = input_img.size
    return extract_pixels(size1, size0, data, "Recreating image...")


def shuffled_axis(pixels, args):
    """Apply vertical shuffling effect."""
    print("Creating array from image...")
    input_img = open_image(args["url"]).convert("RGBA")
    height = input_img.size[1]
    shuffled = array(input_img)

    for _ in get_progress_bar(height, "Shuffling image..."):
        shuffle(shuffled)
    
    print("Saving shuffled image...")
    shuffled_img = Image.fromarray(shuffled, "RGBA")
    data = shuffled_img.load()

    size0, size1 = input_img.size
    return extract_pixels(size1, size0, data, "Recreating image...")


def none(pixels, args):
    """Create single intervals spanning entire rows (no sorting)."""
    intervals = []
    for y in get_progress_bar(len(pixels), "Determining intervals..."):
        intervals.append([len(pixels[y])])
    return intervals


def pixel_sort_image(
    input_path: str,
    output_path: str,
    interval_function: str = "random",
    sorting_function: str = "lightness",
    bottom_threshold: float = 0.25,
    upper_threshold: float = 0.8,
    clength: int = 50,
    angle: float = 0,
    randomness: float = 10
) -> None:
    """Sort pixels in an image using specified parameters.
    
    Args:
        input_path: Path to input image
        output_path: Path for output image
        interval_function: Name of interval function to use
        sorting_function: Name of sorting function to use
        bottom_threshold: Lower threshold for sorting (0-1)
        upper_threshold: Upper threshold for sorting (0-1)
        clength: Characteristic length for random intervals
        angle: Rotation angle in degrees
        randomness: Percentage of intervals NOT to sort (0-100)
    """
    # Clean up old files
    remove_old_file("images/image.png")
    remove_old_file("images/thanos_img.png")
    remove_old_file("images/snapped_pixels.png")
    remove_old_file("images/ElementaryCA.png")
    
    # Get image path
    image_path = get_image_path(input_path)
    
    # Load and process image
    print("Loading image...")
    input_img = open_image(image_path)
    width, height = input_img.size
    print(f"Resolution: {width}x{height}")
    
    # Rotate image if needed
    if angle != 0:
        print("Rotating image...")
        input_img = input_img.rotate(angle, expand=True)
    
    # Extract pixel data
    print("Getting data...")
    data = input_img.load()
    size0, size1 = input_img.size
    pixels = extract_pixels(size1, size0, data, "Getting pixels...")
    
    # Set up parameters
    args = {
        "bottom_threshold": bottom_threshold,
        "upper_threshold": upper_threshold,
        "clength": clength,
        "angle": angle,
        "randomness": randomness,
        "url": image_path
    }
    
    # Get functions
    interval_func = get_interval_function(interval_function)
    sort_func = get_sorting_function(sorting_function)
    
    # Process image
    if interval_function in ["shuffle-total", "shuffle-axis", "snap"]:
        sorted_pixels = interval_func(pixels, args)
    else:
        intervals = interval_func(pixels, args)
        sorted_pixels = sort_image(pixels, intervals, args, sort_func)
    
    # Create output image
    output_img = Image.new("RGBA", input_img.size)
    size0, size1 = output_img.size
    for y in get_progress_bar(size1, "Building output image..."):
        for x in range(size0):
            set_pixel(output_img, x, y, sorted_pixels, y, x)
    
    # Rotate back if needed
    if angle != 0:
        print("Rotating output image back to original orientation...")
        output_img = output_img.rotate(360 - angle, expand=True)
        print("Crop image to appropriate size...")
        output_img = crop_to_reference(output_img, image_path)
    
    # Save image
    print("Saving image...")
    output_img.save(output_path)
    print(f"Image saved to: {output_path}")


def main():
    """Simple main function for basic usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pixelsort.py <input_image> [output_image]")
        print("Example: python pixelsort.py images/default.jpg output/sorted.png")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output/sorted.png"
    
    pixel_sort_image(input_path, output_path)


if __name__ == "__main__":
    main()
