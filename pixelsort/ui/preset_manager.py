"""
Preset management for the pixel sorting application.

This module provides the PresetManager class that handles loading, saving,
and managing custom presets for pixel sorting configurations.
"""

import os
import json
from typing import Tuple
import gradio as gr

from ..config.presets import (
    list_presets, get_preset, 
    create_custom_preset, register_preset, Preset
)
from ..config.settings import AdvancedConfig


class PresetManager:
    """
    Manager class for preset operations in the pixel sorting application.
    
    This class handles loading and saving custom presets, managing the
    custom presets file, and providing preset values for the GUI interface.
    """
    
    def __init__(self, custom_presets_path: str = None):
        """
        Initialize the PresetManager.
        
        Args:
            custom_presets_path: Optional path to custom presets file.
                                If None, uses default location in user's home directory.
        """
        if custom_presets_path is None:
            self.custom_presets_file = os.path.join(
                os.path.expanduser("~"), 
                ".pixelsort_custom_presets.json"
            )
        else:
            self.custom_presets_file = custom_presets_path

    def load_custom_presets(self):
        """Load custom presets from file."""
        try:
            if os.path.exists(self.custom_presets_file):
                with open(self.custom_presets_file, 'r') as f:
                    custom_presets_data = json.load(f)
                    for preset_data in custom_presets_data:
                        preset = Preset.from_dict(preset_data)
                        register_preset(preset)
        except Exception as e:
            print(f"Error loading custom presets: {e}")

    def save_custom_presets(self):
        """Save custom presets to file."""
        try:
            # Get all presets and filter for custom ones (not built-in)
            all_preset_names = list_presets()
            built_in_presets = {'main', 'file', 'random', 'kims', 'gentle', 'intense', 'waves', 'edges'}
            
            custom_preset_data = []
            for preset_name in all_preset_names:
                if preset_name not in built_in_presets:
                    preset = get_preset(preset_name)
                    if preset:
                        custom_preset_data.append(preset.to_dict())
            
            with open(self.custom_presets_file, 'w') as f:
                json.dump(custom_preset_data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom presets: {e}")

    def load_preset_values(self, preset_name: str):
        """
        Load preset values and return them for updating GUI controls.
        
        Args:
            preset_name: Name of preset to load
            
        Returns:
            Tuple of values for GUI controls
        """
        if not preset_name or preset_name == "Select a preset...":
            return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), 
                   gr.update(), gr.update(), gr.update(), "")
        
        preset = get_preset(preset_name)
        if not preset:
            return (gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), 
                   gr.update(), gr.update(), gr.update(), f"❌ Preset '{preset_name}' not found")
        
        config = preset.sorting_config
        
        # Get CA rule from advanced config if available, otherwise use default
        ca_rule_value = -1
        if preset.advanced_config and hasattr(preset.advanced_config, 'ca_rule') and preset.advanced_config.ca_rule is not None:
            ca_rule_value = preset.advanced_config.ca_rule
        
        # Return values for all the GUI controls
        return (
            config.interval_function,           # interval_dropdown
            config.sorting_function,            # sorting_dropdown
            config.randomness,                  # randomness_slider
            config.angle,                       # angle_slider
            config.bottom_threshold,            # bottom_threshold_slider
            config.upper_threshold,             # upper_threshold_slider
            config.clength,                     # characteristic_length_slider
            ca_rule_value,                      # ca_rule_slider
            f"✅ Loaded preset: {preset.name} - {preset.description}"  # status message
        )

    def save_current_as_preset(self, preset_name: str, interval_function: str, sorting_function: str, 
                             randomness: float, angle: float, bottom_threshold: float, 
                             upper_threshold: float, characteristic_length: int, ca_rule_number: int):
        """
        Save current settings as a new preset.
        
        Args:
            preset_name: Name for the new preset
            interval_function: Current interval function
            sorting_function: Current sorting function
            randomness: Current randomness value
            angle: Current rotation angle
            bottom_threshold: Current bottom threshold
            upper_threshold: Current upper threshold
            characteristic_length: Current characteristic length
            ca_rule_number: Current CA rule number
            
        Returns:
            Tuple of (updated preset choices, status message)
        """
        if not preset_name or preset_name.strip() == "":
            return gr.update(), "❌ Please enter a preset name"
        
        preset_name = preset_name.strip()
        
        # Check if preset already exists
        if get_preset(preset_name):
            return gr.update(), f"❌ Preset '{preset_name}' already exists"
        
        try:
            # Create advanced config if CA rule is specified
            advanced_config = None
            if ca_rule_number != -1:
                advanced_config = AdvancedConfig(ca_rule=ca_rule_number)
            
            # Create custom preset
            custom_preset = create_custom_preset(
                name=preset_name,
                description=f"Custom preset: {preset_name}",
                bottom_threshold=bottom_threshold,
                upper_threshold=upper_threshold,
                clength=characteristic_length,
                randomness=randomness,
                angle=angle,
                interval_function=interval_function,
                sorting_function=sorting_function
            )
            
            # Add advanced config if needed
            if advanced_config:
                custom_preset.advanced_config = advanced_config
            
            # Register the preset
            register_preset(custom_preset)
            
            # Save to file
            self.save_custom_presets()
            
            # Update dropdown choices
            preset_choices = ["Select a preset..."] + list_presets()
            
            return gr.update(choices=preset_choices), f"✅ Saved preset: {preset_name}"
            
        except Exception as e:
            return gr.update(), f"❌ Error saving preset: {str(e)}"