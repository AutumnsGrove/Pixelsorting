"""
Configuration classes for pixel sorting operations.

This module contains dataclasses that define all configuration
parameters for sorting operations and image handling.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import os


@dataclass
class SortingConfig:
    """
    Configuration class for pixel sorting parameters.
    
    This class contains all the parameters that control how pixels
    are sorted, including thresholds, intervals, and randomness.
    """
    # Threshold parameters for interval detection
    bottom_threshold: float = 0.25  # Lower lightness threshold (0.0-1.0)
    upper_threshold: float = 0.8    # Upper lightness threshold (0.0-1.0)
    
    # Interval generation parameters
    clength: int = 50               # Characteristic length for random intervals
    randomness: float = 10.0        # Percentage of intervals not to sort (0-100)
    
    # Image transformation parameters
    angle: float = 0.0              # Rotation angle in degrees (0-360)
    
    # Function selection
    interval_function: str = "random"    # Name of interval function to use
    sorting_function: str = "lightness"  # Name of sorting function to use
    
    # Preset configuration
    preset: bool = False            # Whether using a preset
    presetname: str = "None"        # Name of preset being used
    
    def validate(self) -> bool:
        """
        Validate the sorting configuration parameters.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if not (0.0 <= self.bottom_threshold <= 1.0):
            raise ValueError(f"bottom_threshold must be between 0.0 and 1.0, got {self.bottom_threshold}")
        
        if not (0.0 <= self.upper_threshold <= 1.0):
            raise ValueError(f"upper_threshold must be between 0.0 and 1.0, got {self.upper_threshold}")
        
        if self.bottom_threshold >= self.upper_threshold:
            raise ValueError("bottom_threshold must be less than upper_threshold")
        
        if self.clength < 0:
            raise ValueError(f"clength must be non-negative, got {self.clength}")
        
        if not (0.0 <= self.randomness <= 100.0):
            raise ValueError(f"randomness must be between 0.0 and 100.0, got {self.randomness}")
        
        if not (0.0 <= self.angle < 360.0):
            raise ValueError(f"angle must be between 0.0 and 360.0, got {self.angle}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "bottom_threshold": self.bottom_threshold,
            "upper_threshold": self.upper_threshold,
            "clength": self.clength,
            "randomness": self.randomness,
            "angle": self.angle,
            "interval_function": self.interval_function,
            "sorting_function": self.sorting_function,
            "preset": self.preset,
            "presetname": self.presetname,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SortingConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            SortingConfig instance
        """
        # Filter out keys that don't exist in the dataclass
        valid_keys = set(cls.__dataclass_fields__.keys())
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        return cls(**filtered_dict)


@dataclass 
class ImageConfig:
    """
    Configuration class for image input and output parameters.
    
    This class handles all image-related configuration including
    source URLs, file paths, and output settings.
    """
    # Image source parameters
    url: str = ""                   # Image URL or file path
    internet: bool = True           # Whether internet is available
    
    # Legacy database preset parameters (deprecated but kept for compatibility)
    dbpreset: bool = False          # Whether using database preset
    filelink: str = ""              # File image link for database presets
    
    # Output parameters
    output_path: str = "output/"    # Directory for output images
    output_filename: str = ""       # Specific output filename (empty for auto-generated)
    
    # Image processing parameters
    crop_to_reference: bool = False # Whether to crop output to reference image size
    reference_image_url: str = ""   # URL of reference image for cropping
    
    def get_output_filepath(self, base_filename: str = None) -> str:
        """
        Get the complete output file path.
        
        Args:
            base_filename: Base filename to use if output_filename is empty
            
        Returns:
            Complete file path for output image
        """
        if self.output_filename:
            filename = self.output_filename
        elif base_filename:
            filename = base_filename
        else:
            from datetime import datetime
            import random
            import string
            
            # Generate random filename with timestamp
            random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            timestamp = datetime.now().strftime("(%m%d%Y%H%M)")
            filename = f"{random_id}_{timestamp}.png"
        
        # Ensure .png extension
        if not filename.endswith('.png'):
            filename += '.png'
            
        return os.path.join(self.output_path, filename)
    
    def validate(self) -> bool:
        """
        Validate the image configuration parameters.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If any parameter is invalid
        """
        # Only require URL/filelink if this config will be used for actual processing
        # Preset configs may not have URLs until they're applied to a base config
        
        if self.output_path and not os.path.exists(self.output_path):
            try:
                os.makedirs(self.output_path, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create output directory {self.output_path}: {e}")
        
        return True
    
    def validate_for_processing(self) -> bool:
        """
        Validate configuration for actual image processing.
        
        This method performs stricter validation that requires
        a valid image source.
        
        Returns:
            True if configuration is valid for processing
            
        Raises:
            ValueError: If configuration is invalid for processing
        """
        self.validate()  # Run basic validation first
        
        if not self.url and not self.filelink:
            raise ValueError("Either url or filelink must be provided for image processing")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "url": self.url,
            "internet": self.internet,
            "dbpreset": self.dbpreset,
            "filelink": self.filelink,
            "output_path": self.output_path,
            "output_filename": self.output_filename,
            "crop_to_reference": self.crop_to_reference,
            "reference_image_url": self.reference_image_url,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ImageConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            ImageConfig instance
        """
        # Filter out keys that don't exist in the dataclass
        valid_keys = set(cls.__dataclass_fields__.keys())
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        return cls(**filtered_dict)


@dataclass
class AdvancedConfig:
    """
    Configuration class for advanced pixel sorting features.
    
    This class contains experimental and advanced features that
    extend the basic sorting functionality.
    """
    # Experimental features
    enable_cellular_automata: bool = False  # Enable cellular automata generation
    enable_snap_effect: bool = False        # Enable "Thanos snap" effect
    enable_shuffle: bool = False            # Enable pixel shuffling
    
    # Shuffle parameters
    shuffle_mode: str = "none"              # "none", "total", "axis"
    
    # Cellular automata parameters
    ca_rule: Optional[int] = None           # CA rule number (0-255)
    ca_scale_factor: float = 1.0            # Scale factor for CA generation
    
    # Performance parameters
    show_progress: bool = True              # Show progress bars
    parallel_processing: bool = False       # Enable parallel processing (experimental)
    
    # Debugging parameters
    save_intermediate: bool = False         # Save intermediate processing steps
    verbose: bool = False                   # Enable verbose logging
    
    def validate(self) -> bool:
        """
        Validate the advanced configuration parameters.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if self.shuffle_mode not in ["none", "total", "axis"]:
            raise ValueError(f"shuffle_mode must be 'none', 'total', or 'axis', got {self.shuffle_mode}")
        
        if self.ca_rule is not None and not (0 <= self.ca_rule <= 255):
            raise ValueError(f"ca_rule must be between 0 and 255, got {self.ca_rule}")
        
        if self.ca_scale_factor <= 0:
            raise ValueError(f"ca_scale_factor must be positive, got {self.ca_scale_factor}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "enable_cellular_automata": self.enable_cellular_automata,
            "enable_snap_effect": self.enable_snap_effect,
            "enable_shuffle": self.enable_shuffle,
            "shuffle_mode": self.shuffle_mode,
            "ca_rule": self.ca_rule,
            "ca_scale_factor": self.ca_scale_factor,
            "show_progress": self.show_progress,
            "parallel_processing": self.parallel_processing,
            "save_intermediate": self.save_intermediate,
            "verbose": self.verbose,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AdvancedConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            AdvancedConfig instance
        """
        # Filter out keys that don't exist in the dataclass
        valid_keys = set(cls.__dataclass_fields__.keys())
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_keys}
        return cls(**filtered_dict)


@dataclass
class PixelSortConfig:
    """
    Master configuration class that combines all configuration aspects.
    
    This class provides a unified interface to all configuration
    parameters for the pixel sorting system.
    """
    sorting: SortingConfig = field(default_factory=SortingConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)
    
    def validate(self) -> bool:
        """
        Validate all configuration sections.
        
        Returns:
            True if all configurations are valid
            
        Raises:
            ValueError: If any configuration is invalid
        """
        self.sorting.validate()
        self.image.validate()
        self.advanced.validate()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert all configurations to dictionary format.
        
        Returns:
            Dictionary representation of all configurations
        """
        return {
            "sorting": self.sorting.to_dict(),
            "image": self.image.to_dict(),
            "advanced": self.advanced.to_dict(),
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'PixelSortConfig':
        """
        Create master configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            PixelSortConfig instance
        """
        sorting_config = SortingConfig.from_dict(config_dict.get("sorting", {}))
        image_config = ImageConfig.from_dict(config_dict.get("image", {}))
        advanced_config = AdvancedConfig.from_dict(config_dict.get("advanced", {}))
        
        return cls(
            sorting=sorting_config,
            image=image_config,
            advanced=advanced_config
        )
    
    def merge_legacy_args(self, args_dict: Dict[str, Any]) -> None:
        """
        Merge legacy argument dictionary into modern configuration.
        
        This method helps bridge the gap between the old argument
        system and the new configuration system.
        
        Args:
            args_dict: Dictionary with legacy argument names and values
        """
        # Map legacy keys to new configuration structure
        legacy_mapping = {
            # Sorting parameters
            "bottom_threshold": ("sorting", "bottom_threshold"),
            "upper_threshold": ("sorting", "upper_threshold"),
            "clength": ("sorting", "clength"),
            "randomness": ("sorting", "randomness"),
            "angle": ("sorting", "angle"),
            "int_function": ("sorting", "interval_function"),
            "sorting_function": ("sorting", "sorting_function"),
            "preset": ("sorting", "preset"),
            "presetname": ("sorting", "presetname"),
            
            # Image parameters
            "url": ("image", "url"),
            "internet": ("image", "internet"),
            "dbpreset": ("image", "dbpreset"),
            "filelink": ("image", "filelink"),
        }
        
        for legacy_key, (section, new_key) in legacy_mapping.items():
            if legacy_key in args_dict:
                config_section = getattr(self, section)
                setattr(config_section, new_key, args_dict[legacy_key])
    
    def to_legacy_args(self) -> Dict[str, Any]:
        """
        Convert modern configuration back to legacy argument format.
        
        This method helps maintain compatibility with existing code
        that expects the old argument dictionary format.
        
        Returns:
            Dictionary in legacy argument format
        """
        return {
            # Sorting parameters
            "bottom_threshold": self.sorting.bottom_threshold,
            "upper_threshold": self.sorting.upper_threshold,
            "clength": self.sorting.clength,
            "randomness": self.sorting.randomness,
            "angle": self.sorting.angle,
            "int_function": self.sorting.interval_function,
            "sorting_function": self.sorting.sorting_function,
            "preset": self.sorting.preset,
            "presetname": self.sorting.presetname,
            
            # Image parameters
            "url": self.image.url,
            "internet": self.image.internet,
            "dbpreset": self.image.dbpreset,
            "filelink": self.image.filelink,
        }


# Convenience function for creating configurations
def create_config(
    *,
    # Sorting parameters
    bottom_threshold: float = 0.25,
    upper_threshold: float = 0.8,
    clength: int = 50,
    randomness: float = 10.0,
    angle: float = 0.0,
    interval_function: str = "random",
    sorting_function: str = "lightness",
    
    # Image parameters
    url: str = "",
    internet: bool = True,
    output_path: str = "output/",
    
    # Advanced parameters
    show_progress: bool = True,
    verbose: bool = False,
    
    **kwargs
) -> PixelSortConfig:
    """
    Create a pixel sorting configuration with common parameters.
    
    This convenience function allows creating configurations with
    the most commonly used parameters while providing defaults
    for less common ones.
    
    Args:
        bottom_threshold: Lower lightness threshold
        upper_threshold: Upper lightness threshold
        clength: Characteristic length for intervals
        randomness: Percentage of intervals not to sort
        angle: Rotation angle in degrees
        interval_function: Name of interval function
        sorting_function: Name of sorting function
        url: Image URL or file path
        internet: Whether internet is available
        output_path: Output directory path
        show_progress: Whether to show progress bars
        verbose: Whether to enable verbose logging
        **kwargs: Additional parameters
        
    Returns:
        PixelSortConfig instance
    """
    sorting_config = SortingConfig(
        bottom_threshold=bottom_threshold,
        upper_threshold=upper_threshold,
        clength=clength,
        randomness=randomness,
        angle=angle,
        interval_function=interval_function,
        sorting_function=sorting_function,
    )
    
    image_config = ImageConfig(
        url=url,
        internet=internet,
        output_path=output_path,
    )
    
    advanced_config = AdvancedConfig(
        show_progress=show_progress,
        verbose=verbose,
    )
    
    # Apply any additional parameters from kwargs
    for key, value in kwargs.items():
        if hasattr(sorting_config, key):
            setattr(sorting_config, key, value)
        elif hasattr(image_config, key):
            setattr(image_config, key, value)
        elif hasattr(advanced_config, key):
            setattr(advanced_config, key, value)
    
    return PixelSortConfig(
        sorting=sorting_config,
        image=image_config,
        advanced=advanced_config
    )