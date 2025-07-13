"""
Core sorting functionality for pixel sorting operations.

This module contains the main sorting logic that combines interval and sorting functions.
"""

from typing import List, Tuple, Callable
import random as rand
from tqdm import trange

from ..effects.sorting_functions import SortingFunction
from ..effects.interval_functions import IntervalFunction


# Type aliases
PixelArray = List[List[Tuple[int, int, int, int]]]  # 3D array of RGBA pixels
IntervalArray = List[List[int]]  # 2D array of interval boundaries


def sort_interval(pixel_list: List[Tuple[int, int, int, int]], 
                 sorting_function: SortingFunction) -> List[Tuple[int, int, int, int]]:
    """
    Sort a list of pixels using the given sorting function.
    
    Args:
        pixel_list: List of RGBA pixel tuples to sort
        sorting_function: Function to determine sort order
        
    Returns:
        Sorted list of pixels (empty list if input is empty)
    """
    if not pixel_list:
        return []
    return sorted(pixel_list, key=sorting_function)


def sort_image(pixels: PixelArray, intervals: IntervalArray, args: dict, 
               sorting_function: SortingFunction) -> PixelArray:
    """
    Sort pixels in an image based on intervals and sorting function.
    
    Args:
        pixels: 3D array of pixel values
        intervals: 2D array of interval boundaries  
        args: Dictionary containing 'randomness' parameter
        sorting_function: Function to determine pixel sort order
        
    Returns:
        3D array of sorted pixels
    """
    sorted_pixels = []
    
    for y in trange(len(pixels), desc="Sorting...".ljust(30)):
        row = []
        x_min = 0
        
        for x_max in intervals[y]:
            interval = []
            
            # Extract pixels in this interval
            for x in range(int(x_min), int(x_max)):
                if x < len(pixels[y]):
                    interval.append(pixels[y][x])
            
            # Randomly decide whether to sort this interval
            if rand.randint(0, 100) >= args.get("randomness", 0):
                row.extend(sort_interval(interval, sorting_function))
            else:
                row.extend(interval)
            
            x_min = x_max
        
        # Add any remaining pixels
        if len(pixels[y]) > 0 and x_min == 0:
            row.extend([pixels[y][0]])
        
        sorted_pixels.append(row)
    
    return sorted_pixels


def apply_pixel_sort(pixels: PixelArray, interval_function: IntervalFunction,
                    sorting_function: SortingFunction, args: dict) -> PixelArray:
    """
    Apply pixel sorting to an image using specified interval and sorting functions.
    
    Args:
        pixels: 3D array of pixel values
        interval_function: Function to determine sorting intervals
        sorting_function: Function to determine pixel sort order
        args: Dictionary of parameters for the functions
        
    Returns:
        3D array of sorted pixels
    """
    # Generate intervals
    intervals = interval_function(pixels, args)
    
    # Sort pixels within intervals
    sorted_pixels = sort_image(pixels, intervals, args, sorting_function)
    
    return sorted_pixels