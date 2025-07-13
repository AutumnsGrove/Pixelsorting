"""
Interface components for pixel sorting Gradio interface.

This module provides UI component creation logic extracted from the GradioInterface class,
organized into reusable methods for creating different sections of the interface.
"""

import gradio as gr
from typing import List, Tuple, Dict, Any

from ..effects.sorting_functions import list_sorting_functions
from ..effects.interval_functions import list_interval_functions
from ..config.presets import list_presets, get_preset_descriptions


class InterfaceComponents:
    """
    Component factory for creating Gradio interface elements.
    
    This class handles the creation of different sections of the pixel sorting
    interface, including basic options, advanced options, and presets tabs.
    """

    def __init__(self, example_images: List[str] = None):
        """
        Initialize the interface components.
        
        Args:
            example_images: List of paths to example images
        """
        self.example_images = example_images or []
        
        # Get available functions
        self.interval_functions = list_interval_functions()
        self.sorting_functions = list_sorting_functions()
        
        # Get available presets
        self.preset_names = ["Select a preset..."] + list_presets()
        self.preset_descriptions = get_preset_descriptions()

    def create_basic_tab(self) -> Dict[str, Any]:
        """
        Create the basic options tab components.
        
        Returns:
            Dictionary containing all the basic tab components
        """
        components = {}
        
        with gr.Tab("Basic Options"):
            with gr.Row():
                with gr.Column(scale=1):
                    components['input_image'] = gr.Image(
                        type="pil", label="Upload Image", height=400
                    )

                    # Example images
                    if self.example_images:
                        gr.Examples(
                            examples=self.example_images,
                            inputs=components['input_image'],
                            label="Try these examples:",
                        )

                with gr.Column(scale=1):
                    components['output_image'] = gr.Image(
                        type="pil", label="Sorted Image", height=400
                    )

                    components['status_text'] = gr.Textbox(
                        label="Status",
                        placeholder="Upload an image and click 'Sort Pixels' to begin...",
                        interactive=False,
                    )

            # Processing button - moved to top for easy access
            components['process_button'] = gr.Button("Sort Pixels", variant="primary", size="lg")

            with gr.Row():
                components['interval_dropdown'] = gr.Dropdown(
                    choices=self.interval_functions,
                    value="random",
                    label="Interval Function",
                    info="How to group pixels for sorting",
                    scale=1
                )
                components['sorting_dropdown'] = gr.Dropdown(
                    choices=self.sorting_functions,
                    value="lightness",
                    label="Sorting Function",
                    info="How to sort pixels within each group",
                    scale=1
                )
            
            # Add sorting function visualization
            components['sorting_visualization'] = gr.Image(
                label="Sorting Preview",
                type="pil",
                height=120,
                interactive=False,
                show_label=True,
                container=True
            )

            with gr.Row():
                components['randomness_slider'] = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=10,
                    step=1,
                    label="Randomness %",
                    info="Percentage of intervals to leave unsorted",
                )
                components['angle_slider'] = gr.Slider(
                    minimum=0,
                    maximum=359,
                    value=0,
                    step=1,
                    label="Rotation Angle",
                    info="Rotate image before sorting (degrees)",
                    scale=3
                )
                components['angle_visualization'] = gr.Image(
                    label="Angle Preview",
                    type="pil",
                    height=120,
                    width=120,
                    interactive=False,
                    show_label=False,
                    container=False,
                    scale=1
                )
            
            with gr.Row():
                components['scale_slider'] = gr.Slider(
                    minimum=10,
                    maximum=100,
                    value=100,
                    step=5,
                    label="Image Scale %",
                    info="Scale down large images for more visible effects and faster processing"
                )
                components['scale_info'] = gr.Textbox(
                    label="Scaled Dimensions",
                    value="Upload an image to see dimensions",
                    interactive=False,
                    scale=1
                )
        
        return components

    def create_advanced_tab(self) -> Dict[str, Any]:
        """
        Create the advanced options tab components.
        
        Returns:
            Dictionary containing all the advanced tab components
        """
        components = {}
        
        with gr.Tab("Advanced Options"):
            gr.Markdown("### Threshold Parameters")
            gr.Markdown("These parameters control the threshold interval function.")

            with gr.Row():
                components['bottom_threshold_slider'] = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.25,
                    step=0.01,
                    label="Bottom Threshold",
                    info="Lower lightness threshold for interval detection",
                )
                components['upper_threshold_slider'] = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.8,
                    step=0.01,
                    label="Upper Threshold",
                    info="Upper lightness threshold for interval detection",
                )
            
            components['threshold_visualization'] = gr.Image(
                label="Threshold Preview",
                type="pil",
                height=80,
                interactive=False,
                show_label=False,
                container=False
            )
            
            # Add live threshold overlay on uploaded image
            gr.Markdown("### Live Threshold Overlay")
            gr.Markdown("See which pixels will be affected by your threshold settings (like focus peaking on cameras):")
            
            with gr.Row():
                components['overlay_toggle'] = gr.Checkbox(
                    label="Enable Threshold Overlay",
                    value=True,
                    info="Show red/blue overlay on pixels that will be sorted",
                    scale=1
                )
            
            components['threshold_overlay_image'] = gr.Image(
                label="Threshold Overlay Preview",
                type="pil",
                height=300,
                interactive=False,
                show_label=True,
                container=True
            )

            gr.Markdown("### Interval Parameters")
            components['characteristic_length_slider'] = gr.Slider(
                minimum=1,
                maximum=500,
                value=50,
                step=1,
                label="Characteristic Length",
                info="Base length for random and wave intervals",
            )

            gr.Markdown("### Cellular Automata Parameters")
            gr.Markdown(
                "These parameters are used when 'file' or 'file-edges' interval functions are selected."
            )

            with gr.Row():
                components['ca_rule_slider'] = gr.Slider(
                    minimum=-1,
                    maximum=255,
                    value=-1,
                    step=1,
                    label="CA Rule Number",
                    info="Cellular automata rule (0-255). Use -1 for random selection from recommended rules.",
                    scale=3,
                )
                components['ca_preview_button'] = gr.Button("🔍 Preview CA", size="sm", scale=1)

            components['ca_preview_image'] = gr.Image(
                label="Cellular Automata Preview",
                type="pil",
                height=200,
                visible=True,
                interactive=False,
            )

            with gr.Accordion("Recommended CA Rules", open=False):
                gr.Markdown(
                    """
                **Recommended elementary cellular automata rules for interesting patterns:**
                - **Rule 26, 19, 23, 25**: Simple patterns with structure
                - **Rule 35, 106, 11**: More complex organized patterns  
                - **Rule 110**: Turing complete, creates complex structures
                - **Rule 45, 41, 105**: Irregular but structured patterns
                - **Rule 54, 3, 15, 9**: Various geometric patterns
                - **Rule 154, 142**: Dense, fractal-like patterns
                
                Set to -1 to randomly select from these recommended rules, or choose a specific number 0-255.
                """
                )

            # Function descriptions
            gr.Markdown("### Function Descriptions")

            with gr.Accordion("Interval Functions", open=False):
                gr.Markdown(
                    """
                - **random**: Creates intervals of random lengths
                - **threshold**: Creates intervals based on pixel lightness thresholds  
                - **edges**: Uses edge detection to determine intervals
                - **waves**: Creates wave-like intervals with slight randomization
                - **none**: No intervals (sorts entire rows)
                - **file**: Uses cellular automata patterns as interval masks
                - **file-edges**: Uses edge detection on cellular automata patterns
                - **snap**: Thanos snap effect (removes ~50% of pixels randomly)
                - **shuffle-total**: Shuffles pixels within each row
                - **shuffle-axis**: Shuffles the order of rows vertically
                """
                )

            with gr.Accordion("Sorting Functions", open=False):
                gr.Markdown(
                    """
                - **lightness**: Sort by HSV lightness value
                - **intensity**: Sort by sum of RGB values
                - **hue**: Sort by HSV hue value
                - **saturation**: Sort by HSV saturation value
                - **red/green/blue**: Sort by individual color channels
                - **minimum/maximum**: Sort by min/max RGB values
                """
                )
        
        return components

    def create_presets_tab(self) -> Dict[str, Any]:
        """
        Create the presets tab components.
        
        Returns:
            Dictionary containing all the presets tab components
        """
        components = {}
        
        with gr.Tab("Presets"):
            gr.Markdown("### Load Presets")
            gr.Markdown("Choose from built-in presets or your saved custom presets:")
            
            with gr.Row():
                components['preset_dropdown'] = gr.Dropdown(
                    choices=self.preset_names,
                    value="Select a preset...",
                    label="Choose Preset",
                    info="Select a preset to load its settings",
                    scale=2
                )
                components['load_preset_button'] = gr.Button("Load Preset", variant="secondary", scale=1)
            
            # Status for preset loading
            components['preset_status'] = gr.Textbox(
                label="Preset Status",
                value="",
                interactive=False,
                container=False
            )
            
            # Display preset descriptions
            with gr.Accordion("Preset Descriptions", open=False):
                descriptions_text = "\n".join([f"**{name}**: {desc}" for name, desc in self.preset_descriptions.items()])
                gr.Markdown(descriptions_text)
            
            gr.Markdown("---")
            gr.Markdown("### Save Current Settings as Preset")
            gr.Markdown("Save your current advanced settings configuration as a new preset:")
            
            with gr.Row():
                components['new_preset_name'] = gr.Textbox(
                    label="Preset Name",
                    placeholder="Enter a name for your custom preset...",
                    scale=2
                )
                components['save_preset_button'] = gr.Button("💾 Save Preset", variant="primary", scale=1)
            
            components['save_preset_status'] = gr.Textbox(
                label="Save Status",
                value="",
                interactive=False,
                container=False
            )
        
        return components

    def create_main_interface(self) -> Tuple[gr.Blocks, Dict[str, Any]]:
        """
        Create the main interface combining all tabs.
        
        Returns:
            Tuple of (interface, all_components_dict)
        """
        with gr.Blocks(
            title="Pixel Sorter",
            theme=gr.themes.Origin(),
            css=".gradio-container {max-width: 1200px; margin: auto;}",
        ) as interface:

            gr.Markdown("# Pixel Sorter")
            gr.Markdown(
                "Upload an image and experiment with different pixel sorting effects. "
                "Adjust the parameters to create unique visual art!"
            )

            # Create all tabs and collect components
            all_components = {}
            
            # Basic tab
            basic_components = self.create_basic_tab()
            all_components.update(basic_components)
            
            # Advanced tab
            advanced_components = self.create_advanced_tab()
            all_components.update(advanced_components)
            
            # Presets tab
            presets_components = self.create_presets_tab()
            all_components.update(presets_components)

            # Footer
            gr.Markdown(
                "---\n"
                "💡 **Tips:** Start with the basic options, then experiment with advanced parameters. "
                "Different combinations of interval and sorting functions create unique effects! "
                "For large images (>2MB), try scaling down to 25-50% for more visible effects and faster processing. "
                "When using 'file' or 'file-edges' functions, use the Preview CA button to see the cellular automata pattern first."
            )

        return interface, all_components