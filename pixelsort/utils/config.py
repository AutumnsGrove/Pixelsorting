"""
Configuration utilities for pixel sorting operations.

This module contains configuration classes and argument parsing utilities.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SortingConfig:
    """
    Configuration class for pixel sorting parameters.
    """
    # Threshold parameters
    bottom_threshold: float = 0.25
    upper_threshold: float = 0.8
    
    # Interval parameters  
    clength: int = 50  # Characteristic length for random intervals
    randomness: float = 10.0  # Percentage of intervals not to sort
    
    # Image parameters
    angle: float = 0.0  # Rotation angle in degrees
    
    # Function names
    interval_function: str = "random"
    sorting_function: str = "lightness"
    
    # Image source
    url: str = ""
    internet: bool = True
    
    # Preset parameters
    preset: bool = False
    presetname: str = "None"
    dbpreset: bool = False
    filelink: str = ""
    
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
            "int_function": self.interval_function,
            "sorting_function": self.sorting_function,
            "url": self.url,
            "internet": self.internet,
            "preset": self.preset,
            "presetname": self.presetname,
            "dbpreset": self.dbpreset,
            "filelink": self.filelink,
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
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})


def validate_config(config: SortingConfig) -> bool:
    """
    Validate a sorting configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not (0.0 <= config.bottom_threshold <= 1.0):
        raise ValueError("bottom_threshold must be between 0.0 and 1.0")
    
    if not (0.0 <= config.upper_threshold <= 1.0):
        raise ValueError("upper_threshold must be between 0.0 and 1.0")
    
    if config.bottom_threshold >= config.upper_threshold:
        raise ValueError("bottom_threshold must be less than upper_threshold")
    
    if config.clength < 0:
        raise ValueError("clength must be non-negative")
    
    if not (0.0 <= config.randomness <= 100.0):
        raise ValueError("randomness must be between 0.0 and 100.0")
    
    if not (0.0 <= config.angle < 360.0):
        raise ValueError("angle must be between 0.0 and 360.0")
    
    return True