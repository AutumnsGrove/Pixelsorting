"""
Preset configurations for pixel sorting operations.

This module contains predefined configurations that provide
common and interesting pixel sorting effects.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import random as rand

from .settings import SortingConfig, ImageConfig, AdvancedConfig, PixelSortConfig


@dataclass
class Preset:
    """
    A preset configuration for pixel sorting.
    
    This class encapsulates a complete sorting configuration
    with a name and description for easy reuse.
    """
    name: str
    description: str
    sorting_config: SortingConfig
    image_config: Optional[ImageConfig] = None
    advanced_config: Optional[AdvancedConfig] = None
    
    def to_config(self, base_config: Optional[PixelSortConfig] = None) -> PixelSortConfig:
        """
        Convert preset to a complete configuration.
        
        Args:
            base_config: Base configuration to merge with (optional)
            
        Returns:
            Complete PixelSortConfig instance
        """
        if base_config:
            # Merge with existing configuration
            config = PixelSortConfig(
                sorting=base_config.sorting,
                image=base_config.image,
                advanced=base_config.advanced
            )
            
            # Update with preset values
            for field_name, field_value in self.sorting_config.__dict__.items():
                setattr(config.sorting, field_name, field_value)
            
            if self.image_config:
                for field_name, field_value in self.image_config.__dict__.items():
                    if field_value:  # Only override non-empty values
                        setattr(config.image, field_name, field_value)
            
            if self.advanced_config:
                for field_name, field_value in self.advanced_config.__dict__.items():
                    setattr(config.advanced, field_name, field_value)
            
            return config
        else:
            # Create new configuration
            return PixelSortConfig(
                sorting=self.sorting_config,
                image=self.image_config or ImageConfig(),
                advanced=self.advanced_config or AdvancedConfig()
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert preset to dictionary format.
        
        Returns:
            Dictionary representation of the preset
        """
        return {
            "name": self.name,
            "description": self.description,
            "sorting_config": self.sorting_config.to_dict(),
            "image_config": self.image_config.to_dict() if self.image_config else None,
            "advanced_config": self.advanced_config.to_dict() if self.advanced_config else None,
        }
    
    @classmethod
    def from_dict(cls, preset_dict: Dict[str, Any]) -> 'Preset':
        """
        Create preset from dictionary.
        
        Args:
            preset_dict: Dictionary with preset values
            
        Returns:
            Preset instance
        """
        sorting_config = SortingConfig.from_dict(preset_dict.get("sorting_config", {}))
        
        image_config = None
        if preset_dict.get("image_config"):
            image_config = ImageConfig.from_dict(preset_dict["image_config"])
        
        advanced_config = None
        if preset_dict.get("advanced_config"):
            advanced_config = AdvancedConfig.from_dict(preset_dict["advanced_config"])
        
        return cls(
            name=preset_dict["name"],
            description=preset_dict["description"],
            sorting_config=sorting_config,
            image_config=image_config,
            advanced_config=advanced_config
        )


def _generate_random_preset_values() -> Dict[str, Any]:
    """
    Generate random values for preset parameters.
    
    Returns:
        Dictionary with randomized parameter values
    """
    return {
        "randomness": rand.randrange(35, 65),
        "clength": rand.randrange(150, 350, 25),
        "angle": rand.randrange(0, 360),
        "upper_threshold": rand.randrange(50, 100, 5) / 100,
        "bottom_threshold": rand.randrange(10, 50, 5) / 100,
    }


# Define available sorting and interval function options
SORT_FUNC_OPTIONS = ["lightness", "hue", "intensity", "minimum", "saturation"]
INT_FUNC_OPTIONS = [
    "random", "threshold", "edges", "waves", "none",
    "file", "file-edges", "snap", "shuffle-total", "shuffle-axis"
]


# Create preset configurations
PRESETS: Dict[str, Preset] = {}


def _create_main_preset() -> Preset:
    """Create the Main preset with randomized parameters."""
    rand_values = _generate_random_preset_values()
    
    return Preset(
        name="Main",
        description="Main args (r: 35-65, c: random gen, a: 0-360, random, intensity)",
        sorting_config=SortingConfig(
            randomness=rand_values["randomness"],
            clength=rand_values["clength"],
            angle=rand_values["angle"],
            interval_function="random",
            sorting_function="intensity",
            preset=True,
            presetname="Main"
        )
    )


def _create_file_preset() -> Preset:
    """Create the File preset for edge-based sorting."""
    return Preset(
        name="File",
        description="Main args, but only for file edges",
        sorting_config=SortingConfig(
            randomness=rand.randrange(15, 65),
            bottom_threshold=rand.randrange(65, 90) / 100,
            interval_function="edges",
            sorting_function="minimum",
            preset=True,
            presetname="File"
        )
    )


def _create_random_preset() -> Preset:
    """Create the Random preset with complete randomization."""
    rand_values = _generate_random_preset_values()
    
    # Use core interval functions that work reliably
    core_int_funcs = ["random", "threshold", "edges", "waves", "none"]
    
    return Preset(
        name="Random",
        description="Randomness in every arg!",
        sorting_config=SortingConfig(
            angle=rand_values["angle"],
            clength=rand.randrange(50, 500, 25),
            upper_threshold=rand_values["upper_threshold"],
            bottom_threshold=rand_values["bottom_threshold"],
            randomness=rand.randrange(5, 75),
            interval_function=core_int_funcs[rand.randrange(0, len(core_int_funcs))],
            sorting_function=SORT_FUNC_OPTIONS[rand.randrange(0, len(SORT_FUNC_OPTIONS))],
            preset=True,
            presetname="Random"
        )
    )


def _create_kims_preset() -> Preset:
    """Create Kim's preset based on the original processing script."""
    return Preset(
        name="Kims",
        description="Used by Kim Asendorf's original processing script",
        sorting_config=SortingConfig(
            angle=90.0,
            upper_threshold=rand.randrange(15, 85) / 100,
            interval_function="threshold",
            sorting_function=SORT_FUNC_OPTIONS[rand.randrange(0, len(SORT_FUNC_OPTIONS))],
            preset=True,
            presetname="Kims"
        )
    )


def _create_gentle_preset() -> Preset:
    """Create a gentle sorting preset for subtle effects."""
    return Preset(
        name="Gentle",
        description="Subtle sorting with low randomness and small intervals",
        sorting_config=SortingConfig(
            randomness=5.0,
            clength=25,
            angle=0.0,
            bottom_threshold=0.3,
            upper_threshold=0.7,
            interval_function="threshold",
            sorting_function="lightness",
            preset=True,
            presetname="Gentle"
        )
    )


def _create_intense_preset() -> Preset:
    """Create an intense sorting preset for dramatic effects."""
    return Preset(
        name="Intense",
        description="Aggressive sorting with high randomness and large intervals",
        sorting_config=SortingConfig(
            randomness=50.0,
            clength=200,
            angle=45.0,
            bottom_threshold=0.1,
            upper_threshold=0.9,
            interval_function="random",
            sorting_function="hue",
            preset=True,
            presetname="Intense"
        )
    )


def _create_waves_preset() -> Preset:
    """Create a waves preset for organic-looking effects."""
    return Preset(
        name="Waves",
        description="Wave-like intervals for organic flowing effects",
        sorting_config=SortingConfig(
            randomness=20.0,
            clength=75,
            angle=15.0,
            interval_function="waves",
            sorting_function="saturation",
            preset=True,
            presetname="Waves"
        )
    )


def _create_edges_preset() -> Preset:
    """Create an edges preset for edge-detection based sorting."""
    return Preset(
        name="Edges",
        description="Edge detection intervals for structure-aware sorting",
        sorting_config=SortingConfig(
            randomness=15.0,
            bottom_threshold=0.4,
            angle=0.0,
            interval_function="edges", 
            sorting_function="intensity",
            preset=True,
            presetname="Edges"
        )
    )


# Initialize all presets
def _initialize_presets() -> None:
    """Initialize the PRESETS dictionary with all available presets."""
    preset_creators = [
        _create_main_preset,
        _create_file_preset,
        _create_random_preset,
        _create_kims_preset,
        _create_gentle_preset,
        _create_intense_preset,
        _create_waves_preset,
        _create_edges_preset,
    ]
    
    for creator in preset_creators:
        preset = creator()
        PRESETS[preset.name.lower()] = preset
        PRESETS[preset.name] = preset  # Also store with original case


# Initialize presets when module is imported
_initialize_presets()


def get_preset(name: str) -> Optional[Preset]:
    """
    Get a preset by name.
    
    Args:
        name: Name of the preset (case-insensitive)
        
    Returns:
        Preset instance if found, None otherwise
    """
    return PRESETS.get(name.lower())


def list_presets() -> List[str]:
    """
    Get a list of available preset names.
    
    Returns:
        List of preset names
    """
    # Return only lowercase names to avoid duplicates
    return [name for name in PRESETS.keys() if name.islower()]


def get_preset_descriptions() -> Dict[str, str]:
    """
    Get descriptions for all available presets.
    
    Returns:
        Dictionary mapping preset names to descriptions
    """
    return {name: PRESETS[name].description for name in list_presets()}


def create_custom_preset(
    name: str,
    description: str,
    *,
    # Sorting parameters
    bottom_threshold: float = 0.25,
    upper_threshold: float = 0.8,
    clength: int = 50,
    randomness: float = 10.0,
    angle: float = 0.0,
    interval_function: str = "random",
    sorting_function: str = "lightness",
    **kwargs
) -> Preset:
    """
    Create a custom preset with specified parameters.
    
    Args:
        name: Name of the preset
        description: Description of the preset
        bottom_threshold: Lower lightness threshold
        upper_threshold: Upper lightness threshold
        clength: Characteristic length for intervals
        randomness: Percentage of intervals not to sort
        angle: Rotation angle in degrees
        interval_function: Name of interval function
        sorting_function: Name of sorting function
        **kwargs: Additional parameters
        
    Returns:
        Custom Preset instance
    """
    sorting_config = SortingConfig(
        bottom_threshold=bottom_threshold,
        upper_threshold=upper_threshold,
        clength=clength,
        randomness=randomness,
        angle=angle,
        interval_function=interval_function,
        sorting_function=sorting_function,
        preset=True,
        presetname=name
    )
    
    # Apply any additional sorting parameters from kwargs
    for key, value in kwargs.items():
        if hasattr(sorting_config, key):
            setattr(sorting_config, key, value)
    
    return Preset(
        name=name,
        description=description,
        sorting_config=sorting_config
    )


def register_preset(preset: Preset) -> None:
    """
    Register a custom preset in the global preset registry.
    
    Args:
        preset: Preset to register
    """
    PRESETS[preset.name.lower()] = preset
    PRESETS[preset.name] = preset


def get_random_preset() -> Preset:
    """
    Get a randomly selected preset.
    
    Returns:
        Random Preset instance
    """
    preset_names = list_presets()
    if not preset_names:
        # Fallback to Random preset if no presets available
        return _create_random_preset()
    
    random_name = rand.choice(preset_names)
    return PRESETS[random_name]


# Utility function for backward compatibility
def get_legacy_preset_data(preset_name: str) -> tuple:
    """
    Get preset data in legacy format for backward compatibility.
    
    This function returns preset data in the original tuple format
    used by the legacy ReadPreset function.
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        Tuple in legacy format: (args_string, int_func, sort_func, preset_true,
        int_rand, sort_rand, int_chosen, sort_chosen, shuffled, snapped,
        file_sorted, db_preset, db_file_img)
    """
    preset = get_preset(preset_name)
    if not preset:
        # Return default values for unknown preset
        return ("", "", "", False, False, False, False, False, False, False, False, False, "")
    
    config = preset.sorting_config
    
    # Build args string
    args_parts = []
    if config.randomness != 10.0:
        args_parts.append(f"-r {config.randomness}")
    if config.clength != 50:
        args_parts.append(f"-c {config.clength}")
    if config.angle != 0.0:
        args_parts.append(f"-a {config.angle}")
    if config.bottom_threshold != 0.25:
        args_parts.append(f"-t {config.bottom_threshold}")
    if config.upper_threshold != 0.8:
        args_parts.append(f"-u {config.upper_threshold}")
    
    args_string = " ".join(args_parts)
    
    return (
        args_string,                    # arg_parse_input
        config.interval_function,       # int_func_input
        config.sorting_function,        # sort_func_input
        True,                          # preset_true
        False,                         # int_rand (deprecated)
        False,                         # sort_rand (deprecated)
        True,                          # int_chosen
        True,                          # sort_chosen
        False,                         # shuffled (deprecated)
        False,                         # snapped (deprecated)
        config.interval_function in ["file", "file-edges"],  # file_sorted
        False,                         # db_preset (deprecated)
        "",                           # db_file_img (deprecated)
    )