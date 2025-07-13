"""
Visualization components for the pixel sorting application.

This module contains visualization methods for creating interactive previews
and helpful visual aids for the Gradio interface. These components help users
understand how different parameters affect the pixel sorting process.
"""

import math
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw

from ..effects.special_effects import generate_elementary_cellular_automata
from ..effects.sorting_functions import get_sorting_function


class VisualizationComponents:
    """
    Collection of visualization methods for the pixel sorting application.
    
    This class provides static methods for generating various types of
    visualizations including angle previews, threshold overlays, sorting
    function demonstrations, and cellular automata previews.
    """

    @staticmethod
    def preview_cellular_automata(ca_rule_number: int) -> Image.Image:
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

    @staticmethod
    def create_angle_visualization(angle: float) -> Image.Image:
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

    @staticmethod
    def create_threshold_visualization(bottom_threshold: float, upper_threshold: float) -> Image.Image:
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

    @staticmethod
    def create_sorting_function_visualization(sorting_function: str) -> Image.Image:
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

    @staticmethod
    def create_threshold_overlay(image: Image.Image, bottom_threshold: float, upper_threshold: float, overlay_enabled: bool = True) -> Image.Image:
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