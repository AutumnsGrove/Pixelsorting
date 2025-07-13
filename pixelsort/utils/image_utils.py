"""
Image utility functions for pixel sorting operations.

This module contains utilities for opening, processing, and manipulating images
for pixel sorting effects.
"""

from typing import List, Tuple, Union
import os.path
from PIL import Image, ImageFilter
import requests
from tqdm import tqdm, trange

from .exceptions import (
    ImageNotFoundError, ImageLoadError, NetworkError, 
    handle_image_error
)


# Type aliases for clarity
PixelTuple = Tuple[int, int, int, int]  # RGBA values
PixelArray = List[List[PixelTuple]]


def check_url_or_path(input_str: str) -> bool:
    """
    Check if the input string is a valid file path.
    
    Args:
        input_str: The input string, file path or url
        
    Returns:
        True if the file path exists, False if it does not.
    """
    return os.path.exists(input_str)


@handle_image_error
def open_image(url_or_path: str, has_internet: bool = True) -> Image.Image:
    """
    Opens an image from a URL or local file path.
    
    Args:
        url_or_path: The URL or local file path of the image
        has_internet: Whether internet connection is available
        
    Returns:
        PIL Image object in RGBA mode
        
    Raises:
        ImageNotFoundError: If local file is not found
        NetworkError: If URL cannot be loaded
        ImageLoadError: If image cannot be processed
    """
    is_local_file = check_url_or_path(url_or_path)
    
    if not is_local_file and has_internet:
        # Try to open as URL
        try:
            response = requests.get(url_or_path, stream=True, timeout=30)
            response.raise_for_status()
            img = Image.open(response.raw).convert("RGBA")
            return img
        except requests.RequestException as e:
            raise NetworkError(url_or_path, e)
        except Exception as e:
            raise ImageLoadError(f"Failed to process image from URL", url_or_path, e)
    else:
        # Open as local file
        if not os.path.exists(url_or_path):
            raise ImageNotFoundError(url_or_path)
        
        try:
            img = Image.open(url_or_path).convert("RGBA")
            return img
        except Exception as e:
            raise ImageLoadError(f"Failed to load local image file", url_or_path, e)


def image_to_pixel_array(width: int, height: int, pixel_data, progress_msg: str) -> PixelArray:
    """
    Convert a PIL image's pixel data to a 3D array of pixel values.
    
    Args:
        width: Image width
        height: Image height  
        pixel_data: PixelAccess object from img.load()
        progress_msg: Message to display in progress bar
        
    Returns:
        3D array of pixel values [y][x] = (r, g, b, a)
    """
    pixels = []
    
    for y in trange(height, desc=f"{progress_msg:30}"):
        row = []
        for x in range(width):
            row.append(pixel_data[x, y])
        pixels.append(row)
    
    return pixels


def crop_to_reference(image_to_crop: Image.Image, reference_image: Image.Image) -> Image.Image:
    """
    Crop an image to match the size of a reference image.
    
    Assumes the relevant content is centered and crops equal amounts from
    both sides (left/right and top/bottom).
    
    Args:
        image_to_crop: The image to be cropped
        reference_image: The reference image to match size to
        
    Returns:
        Cropped image matching the reference size
    """
    reference_size = reference_image.size
    current_size = image_to_crop.size
    
    dx = current_size[0] - reference_size[0]
    dy = current_size[1] - reference_size[1]
    
    left = dx / 2
    upper = dy / 2
    right = dx / 2 + reference_size[0]
    lower = dy / 2 + reference_size[1]
    
    return image_to_crop.crop(box=(int(left), int(upper), int(right), int(lower)))


def set_pixel(image: Image.Image, x: int, y: int, pixel_data: PixelArray) -> None:
    """
    Set a pixel in a PIL Image from pixel array data.
    
    Args:
        image: PIL Image to modify
        x: X coordinate
        y: Y coordinate
        pixel_data: 3D array of pixel values
    """
    image.putpixel((x, y), pixel_data[y][x])


def append_pixel_from_image(pixel_list: List[List[PixelTuple]], x: int, y: int, 
                           image_data) -> None:
    """
    Append a pixel from image data to a pixel list.
    
    Args:
        pixel_list: The list to append to
        x: X coordinate
        y: Y coordinate  
        image_data: PixelAccess object from PIL Image
    """
    pixel_list[y].append(image_data[x, y])


def rotate_image(image: Image.Image, angle: float) -> Image.Image:
    """
    Rotate an image by the specified angle.
    
    Args:
        image: PIL Image to rotate
        angle: Rotation angle in degrees
        
    Returns:
        Rotated image with expanded bounds
    """
    return image.rotate(angle, expand=True)


def apply_edge_filter(image: Image.Image) -> Image.Image:
    """
    Apply edge detection filter to an image.
    
    Args:
        image: PIL Image to filter
        
    Returns:
        Edge-filtered image in RGBA mode
    """
    return image.filter(ImageFilter.FIND_EDGES).convert("RGBA")