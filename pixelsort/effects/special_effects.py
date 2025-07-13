"""
Special effects for pixel sorting operations.

This module contains special effects like Elementary Cellular Automata generation,
Thanos snap effect, and shuffle effects. All functions return PIL Images without
performing file I/O operations.
"""

import random as rand
from typing import Dict, Any, Tuple, List
from PIL import Image
import numpy as np
from numpy import array, mgrid
from numpy.random import choice, shuffle
from tqdm import trange

from ..utils.image_utils import open_image, image_to_pixel_array


def generate_elementary_cellular_automata(width: int, height: int, 
                                        rule_number: int = None) -> Image.Image:
    """
    Generate images of elementary cellular automata.
    
    Selected rules from https://en.wikipedia.org/wiki/Elementary_cellular_automaton
    
    Args:
        width: Width of the generated image
        height: Height of the generated image
        rule_number: Optional rule number (0-255). If None, a random recommended rule is chosen.
        
    Returns:
        PIL Image object containing the cellular automaton
    """
    # Scale down for performance on large images
    scaled_width = width // 4 if width <= 2500 else width // 8
    scaled_height = height // 4 if height <= 2500 else height // 8
    
    # Recommended rules that produce interesting patterns
    recommended_rules = [26, 19, 23, 25, 35, 106, 11, 110, 45, 41, 105, 54, 3, 15, 9, 154, 142]
    
    if rule_number is None:
        rule_number = recommended_rules[rand.randrange(0, len(recommended_rules))]
    elif rule_number not in range(256):
        print(f"Rule number {rule_number} not in range 0-255, using random rule.")
        rule_number = recommended_rules[rand.randrange(0, len(recommended_rules))]
    
    # Define colors of the output image
    true_pixel = (255, 255, 255)
    false_pixel = (0, 0, 0)
    
    def generate_rule(rule_num: int) -> Dict[Tuple[bool, bool, bool], bool]:
        """
        Generate a dictionary that tells you what your state should be based on the rule number
        and the states of the adjacent cells in the previous generation.
        """
        rule = {}
        for left in [False, True]:
            for middle in [False, True]:
                for right in [False, True]:
                    rule[(left, middle, right)] = rule_num % 2 == 1
                    rule_num //= 2
        return rule
    
    def generate_ca(rule: Dict[Tuple[bool, bool, bool], bool]) -> list:
        """
        Generate a 2D representation of the state of the automaton at each generation.
        """
        ca = []
        
        # Initialize the first row of ca randomly
        ca.append([])
        for x in range(int(scaled_width)):
            ca[0].append(bool(rand.getrandbits(1)))
        
        # Generate the succeeding generations
        # Cells at the edges are initialized randomly
        for y in range(1, int(scaled_height)):
            ca.append([])
            ca[y].append(bool(rand.getrandbits(1)))  # Left edge
            
            for x in range(1, int(scaled_width) - 1):
                left_state = ca[y - 1][x - 1]
                middle_state = ca[y - 1][x]
                right_state = ca[y - 1][x + 1]
                new_state = rule[(left_state, middle_state, right_state)]
                ca[y].append(new_state)
            
            ca[y].append(bool(rand.getrandbits(1)))  # Right edge
        
        return ca
    
    # Generate the rule and cellular automaton
    rule = generate_rule(rule_number)
    ca = generate_ca(rule)
    
    # Create the image
    new_img = Image.new("RGB", [int(scaled_width), int(scaled_height)])
    
    print(f"Creating Elementary CA image... Rule: {rule_number}")
    for y in trange(int(scaled_height), desc="Placing pixels...".ljust(30)):
        for x in range(int(scaled_width)):
            pixel_color = true_pixel if ca[y][x] else false_pixel
            new_img.putpixel((x, y), pixel_color)
    
    print("Elementary CA image created!")
    
    # Resize to requested dimensions if different from scaled dimensions
    if (scaled_width, scaled_height) != (width, height):
        new_img = new_img.resize((width, height), Image.ANTIALIAS)
    
    return new_img


def apply_thanos_snap(image: Image.Image) -> Image.Image:
    """
    Apply the Thanos snap effect to an image.
    
    This effect randomly removes approximately half of the pixels from the image,
    setting them to transparent.
    
    Args:
        image: PIL Image to apply the effect to
        
    Returns:
        PIL Image with snap effect applied
    """
    print("The hardest choices require the strongest wills...")
    
    # Convert to RGBA to support transparency
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Convert to numpy array for efficient processing
    pixels_snap = array(image)
    
    # Get image dimensions
    nx, ny = image.size
    
    # Create coordinate grid
    xy = mgrid[:nx, :ny].reshape(2, -1).T
    
    # Calculate how many pixels to snap (half)
    total_pixels = xy.shape[0]
    snapped_count = int(round(total_pixels / 2, 0))
    
    # Randomly select pixels to snap
    pixels_to_snap = xy.take(
        choice(xy.shape[0], snapped_count, replace=False), axis=0
    )
    
    print(f'Number of those worthy of the sacrifice: {("{:,}".format(snapped_count))}')
    
    # Apply the snap effect
    for i in trange(len(pixels_to_snap), desc="Snapping...".ljust(30)):
        x, y = pixels_to_snap[i]
        pixels_snap[y][x] = [0, 0, 0, 0]  # Set to transparent
    
    print("Perfectly balanced, as all things should be.")
    print("/" * 45)
    
    # Convert back to PIL Image
    snapped_image = Image.fromarray(pixels_snap, "RGBA")
    return snapped_image


def shuffle_image_rows(image: Image.Image) -> Image.Image:
    """
    Shuffle pixels within each row of the image.
    
    Args:
        image: PIL Image to shuffle
        
    Returns:
        PIL Image with shuffled rows
    """
    print("Creating array from image...")
    
    # Convert to RGBA if needed
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Convert to numpy array
    shuffled = array(image)
    height = image.size[1]
    
    # Shuffle each row independently
    for i in trange(int(height), desc="Shuffling image rows...".ljust(30)):
        shuffle(shuffled[i])
    
    print("Row shuffling complete!")
    
    # Convert back to PIL Image
    shuffled_img = Image.fromarray(shuffled, "RGBA")
    return shuffled_img


def shuffle_image_vertically(image: Image.Image) -> Image.Image:
    """
    Shuffle the image vertically (shuffle the order of rows).
    
    Args:
        image: PIL Image to shuffle
        
    Returns:
        PIL Image with vertically shuffled rows
    """
    print("Creating array from image...")
    
    # Convert to RGBA if needed
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Convert to numpy array
    shuffled = array(image)
    height = image.size[1]
    
    # Shuffle the entire array vertically (rows)
    for _ in trange(height, desc="Shuffling image vertically...".ljust(30)):
        shuffle(shuffled)
    
    print("Vertical shuffling complete!")
    
    # Convert back to PIL Image
    shuffled_img = Image.fromarray(shuffled, "RGBA")
    return shuffled_img


def create_special_effect_image(effect_type: str, width: int, height: int, 
                               base_image: Image.Image = None, **kwargs) -> Image.Image:
    """
    Factory function to create special effect images.
    
    Args:
        effect_type: Type of effect ("cellular_automata", "thanos_snap", "shuffle_rows", "shuffle_vertical")
        width: Width for generated images (ignored for effects applied to existing images)
        height: Height for generated images (ignored for effects applied to existing images)
        base_image: Base image for effects that modify existing images
        **kwargs: Additional arguments for specific effects
        
    Returns:
        PIL Image with the applied effect
        
    Raises:
        ValueError: If effect_type is unknown or required parameters are missing
    """
    if effect_type == "cellular_automata":
        rule_number = kwargs.get("rule_number", None)
        return generate_elementary_cellular_automata(width, height, rule_number)
    
    elif effect_type == "thanos_snap":
        if base_image is None:
            raise ValueError("thanos_snap effect requires a base_image")
        return apply_thanos_snap(base_image)
    
    elif effect_type == "shuffle_rows":
        if base_image is None:
            raise ValueError("shuffle_rows effect requires a base_image")
        return shuffle_image_rows(base_image)
    
    elif effect_type == "shuffle_vertical":
        if base_image is None:
            raise ValueError("shuffle_vertical effect requires a base_image")
        return shuffle_image_vertically(base_image)
    
    else:
        available_effects = ["cellular_automata", "thanos_snap", "shuffle_rows", "shuffle_vertical"]
        raise ValueError(f"Unknown effect type '{effect_type}'. Available: {', '.join(available_effects)}")


# Registry of available special effects
SPECIAL_EFFECTS = {
    "cellular_automata": generate_elementary_cellular_automata,
    "thanos_snap": apply_thanos_snap,
    "shuffle_rows": shuffle_image_rows,
    "shuffle_vertical": shuffle_image_vertically,
}


def list_special_effects() -> List[str]:
    """
    Get a list of available special effects.
    
    Returns:
        List of special effect names
    """
    return list(SPECIAL_EFFECTS.keys())