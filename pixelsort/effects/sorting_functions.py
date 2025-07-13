"""
Sorting functions for pixel sorting operations.

This module contains functions that determine how pixels are sorted
based on their color properties.
"""

from typing import Tuple, Callable, Dict, List
from colorsys import rgb_to_hsv


# Type aliases
PixelTuple = Tuple[int, int, int, int]  # RGBA values
SortingFunction = Callable[[PixelTuple], float]


def lightness_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by lightness (HSV value component).
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Lightness value between 0.0 and 1.0
    """
    r, g, b = pixel[0] / 255.0, pixel[1] / 255.0, pixel[2] / 255.0
    return rgb_to_hsv(r, g, b)[2]


def intensity_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by RGB intensity (sum of RGB values).
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Sum of RGB values
    """
    return pixel[0] + pixel[1] + pixel[2]


def hue_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by hue (HSV hue component).
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Hue value between 0.0 and 1.0
    """
    r, g, b = pixel[0] / 255.0, pixel[1] / 255.0, pixel[2] / 255.0
    return rgb_to_hsv(r, g, b)[0]


def saturation_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by saturation (HSV saturation component).
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Saturation value between 0.0 and 1.0
    """
    r, g, b = pixel[0] / 255.0, pixel[1] / 255.0, pixel[2] / 255.0
    return rgb_to_hsv(r, g, b)[1]


def minimum_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by minimum RGB value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Minimum of RGB values
    """
    return min(pixel[0], pixel[1], pixel[2])


def red_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by red channel value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Red channel value
    """
    return pixel[0]


def green_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by green channel value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Green channel value
    """
    return pixel[1]


def blue_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by blue channel value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Blue channel value
    """
    return pixel[2]


def alpha_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by alpha (transparency) channel value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Alpha channel value
    """
    return pixel[3]


def maximum_sort(pixel: PixelTuple) -> float:
    """
    Sort pixels by maximum RGB value.
    
    Args:
        pixel: RGBA pixel tuple (r, g, b, a)
        
    Returns:
        Maximum of RGB values
    """
    return max(pixel[0], pixel[1], pixel[2])


# Registry of available sorting functions
SORTING_FUNCTIONS: Dict[str, SortingFunction] = {
    "lightness": lightness_sort,
    "intensity": intensity_sort,
    "hue": hue_sort,
    "saturation": saturation_sort,
    "minimum": minimum_sort,
    "red": red_sort,
    "green": green_sort,
    "blue": blue_sort,
    "alpha": alpha_sort,
    "maximum": maximum_sort,
}


def get_sorting_function(name: str) -> SortingFunction:
    """
    Get a sorting function by name.
    
    Args:
        name: Name of the sorting function
        
    Returns:
        Sorting function
        
    Raises:
        FunctionNotFoundError: If the sorting function name is not found
    """
    if name not in SORTING_FUNCTIONS:
        from ..utils.exceptions import raise_function_not_found
        raise_function_not_found("sorting", name, list(SORTING_FUNCTIONS.keys()))
    
    return SORTING_FUNCTIONS[name]


def list_sorting_functions() -> List[str]:
    """
    Get a list of available sorting function names.
    
    Returns:
        List of sorting function names
    """
    return list(SORTING_FUNCTIONS.keys())