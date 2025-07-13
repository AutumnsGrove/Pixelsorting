"""
Configuration module for pixel sorting operations.

This module provides configuration classes and preset management
for the pixel sorting library.
"""

from .settings import (
    SortingConfig, 
    ImageConfig, 
    AdvancedConfig,
    PixelSortConfig,
    create_config
)
from .presets import (
    Preset, 
    PRESETS, 
    get_preset,
    list_presets,
    get_preset_descriptions,
    create_custom_preset,
    register_preset,
    get_random_preset,
    get_legacy_preset_data
)

__all__ = [
    # Configuration classes
    'SortingConfig',
    'ImageConfig', 
    'AdvancedConfig',
    'PixelSortConfig',
    'create_config',
    
    # Preset management
    'Preset',
    'PRESETS',
    'get_preset',
    'list_presets',
    'get_preset_descriptions',
    'create_custom_preset',
    'register_preset',
    'get_random_preset',
    'get_legacy_preset_data'
]