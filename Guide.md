# Pixel Sort Refactoring Guide

## Overview
This guide provides step-by-step instructions for refactoring the pixelsort.py monolithic application into a modern, modular Python application with a Gradio web interface.

## Phase 1: Project Analysis and Setup

### Step 1: Initial Assessment
1. Open the original `pixelsort.py` file
2. Create a new file called `analysis.md` and document:
   - List all the main functions and their purposes (use regex search for `^def `)
   - Identify all lambda functions and their uses
   - Find all hardcoded values (URLs, API keys, magic numbers)
   - Locate all `input()` calls and user interaction points
   - Search for commented-out or deprecated code sections

### Step 2: Dependency Audit
1. Create a new `requirements.txt` with modern versions:
   ```
   pillow>=10.0.0
   numpy>=1.24.0
   tqdm>=4.65.0
   gradio>=4.0.0
   ```
2. Remove `requests` dependency (no longer needed without uploads)
3. Document which functions use which dependencies

### Step 3: Create Project Structure
```bash
mkdir -p pixelsort/{core,effects,utils,ui,config}
touch pixelsort/__init__.py
touch pixelsort/{core,effects,utils,ui,config}/__init__.py
```

## Phase 2: Extract Core Components

### Step 4: Extract Image Utilities
1. Create `pixelsort/utils/image_utils.py`
2. Move these functions (maintaining their logic but cleaning up style):
   - `ImgOpen()` → `open_image()` (remove upload logic)
   - `PixelAppend()` → `image_to_pixel_array()`
   - `CropTo()` → `crop_to_reference()`
   - Image rotation logic from main
3. Replace lambdas with proper functions:
   - Convert `ImgPixels` lambda to `set_pixel()`
   - Convert `AppendPIL` lambda to a clear function
4. Add type hints and improve docstrings

### Step 5: Extract Sorting Functions
1. Create `pixelsort/effects/sorting_functions.py`
2. Move all sorting lambdas as proper functions:
   ```python
   def sort_by_lightness(pixel: Tuple[int, int, int, int]) -> float:
       """Sort pixels by their lightness value."""
       return rgb_to_hsv(pixel[0], pixel[1], pixel[2])[2] / 255.0
   ```
3. Create a registry dictionary:
   ```python
   SORTING_FUNCTIONS = {
       'lightness': sort_by_lightness,
       'hue': sort_by_hue,
       # etc.
   }
   ```

### Step 6: Extract Interval Functions
1. Create `pixelsort/effects/interval_functions.py`
2. Move each interval function (`edge`, `threshold`, `random`, etc.)
3. Standardize their signatures:
   ```python
   def interval_random(pixels: np.ndarray, config: 'SortingConfig') -> List[List[int]]:
   ```
4. Create an interval function registry similar to sorting functions

## Phase 3: Configuration Management

### Step 7: Create Configuration Classes
1. Create `pixelsort/config/settings.py`:
   ```python
   from dataclasses import dataclass
   from typing import Optional

   @dataclass
   class SortingConfig:
       interval_function: str = "random"
       sorting_function: str = "lightness"
       randomness: float = 0.0
       angle: float = 0.0
       threshold_lower: float = 0.25
       threshold_upper: float = 0.8
       characteristic_length: int = 50
       
   @dataclass
   class ImageConfig:
       input_path: Optional[str] = None
       output_path: str = "output.png"
   ```

### Step 8: Extract Presets
1. Create `pixelsort/config/presets.py`
2. Convert the `presets` dictionary to a cleaner format
3. Remove database preset functionality
4. Create a `Preset` dataclass for type safety

## Phase 4: Core Processing Logic

### Step 9: Create Main Processor
1. Create `pixelsort/core/processor.py`
2. Extract the core sorting logic from `SortImage()`:
   ```python
   class PixelSorter:
       def __init__(self, config: SortingConfig):
           self.config = config
           
       def process(self, image: Image.Image) -> Image.Image:
           # Main processing pipeline
   ```
3. Break down the main processing into clear steps:
   - `prepare_image()` (rotation, conversion)
   - `generate_intervals()`
   - `sort_pixels()`
   - `reconstruct_image()`

### Step 10: Clean Up Special Effects
1. Create `pixelsort/effects/special_effects.py`
2. Move and refactor:
   - Elementary Cellular Automata generation
   - Thanos snap effect
   - Shuffle effects
3. Remove file I/O from these functions - they should return PIL Images

## Phase 5: User Interface Migration

### Step 11: Create Gradio Interface
1. Create `pixelsort/ui/gradio_interface.py`
2. Design the interface structure:
   ```python
   def create_interface():
       with gr.Blocks(title="Pixel Sorter") as interface:
           # Add tabs for basic/advanced options
           # Include preset dropdown
           # Add before/after image comparison
   ```
3. Map all command-line arguments to Gradio components
4. Add example images (store locally, not as URLs)

### Step 12: Create Processing Endpoint
1. In the Gradio interface, create a main processing function:
   ```python
   def process_image(
       image,
       interval_func,
       sorting_func,
       angle,
       randomness,
       # ... other parameters
   ):
       config = SortingConfig(...)
       sorter = PixelSorter(config)
       return sorter.process(image)
   ```

### Step 13: Add Progress Tracking
1. Replace tqdm progress bars with Gradio progress
2. Use `gr.Progress()` for long operations
3. Add status messages for each processing step

## Phase 6: Cleanup and Modernization (1 hour)

### Step 14: Remove Legacy Code
1. Delete all upload-related functions
2. Remove database interaction code
3. Remove the `misc_variables` dictionary
4. Clean up the argument parsing code
5. Remove `clear()` and other CLI-specific functions

### Step 15: Improve Code Quality
1. Run through each module and:
   - Convert all function names to snake_case
   - Add comprehensive type hints
   - Replace string concatenation with f-strings
   - Remove unused imports
   - Standardize docstring format (Google style)

### Step 16: Error Handling
1. Create `pixelsort/utils/exceptions.py`:
   ```python
   class PixelSortError(Exception):
       """Base exception for pixel sorting errors."""
       
   class InvalidImageError(PixelSortError):
       """Raised when image cannot be processed."""
   ```
2. Replace generic try/except blocks with specific error handling

## Phase 7: Testing and Documentation

### Step 17: Create Test Structure
1. Create `tests/` directory
2. Write basic tests for:
   - Image loading/saving
   - Each sorting function
   - Each interval function
   - Configuration validation

### Step 18: Update Documentation
1. Create a new `README.md` with:
   - Installation instructions (uv pip install)
   - Gradio interface usage
   - Example outputs
   - Configuration options
2. Remove references to:
   - Command-line usage
   - Upload functionality
   - Database presets

### Step 19: Create Entry Point
1. Create `pixelsort/main.py`:
   ```python
   from pixelsort.ui.gradio_interface import create_interface
   
   def main():
       interface = create_interface()
       interface.launch()
       
   if __name__ == "__main__":
       main()
   ```

### Step 20: Final Integration
1. Create `setup.py` for package installation
2. Test the complete pipeline with sample images
3. Ensure all features work through the Gradio interface

## Implementation Notes

### Priority Order
1. Start with Phase 2 (Extract Core Components) - this creates the foundation
2. Then Phase 4 (Core Processing Logic) - this ensures the refactoring works
3. Follow with Phase 5 (UI Migration) - this makes it usable
4. Complete remaining phases for polish

### Key Principles
- **Incremental Refactoring**: Test after each major change
- **Preserve Functionality**: All original features should work
- **Improve Readability**: Clear names, good structure
- **Modern Python**: Use dataclasses, type hints, pathlib
- **User-Friendly**: Gradio should be easier than CLI

### Common Pitfalls to Avoid
1. Don't try to refactor everything at once
2. Keep the math/algorithm logic intact - just reorganize it
3. Test image processing after each phase
4. Don't forget to handle edge cases (empty intervals, invalid images)

### Success Metrics
- [ ] All functions have type hints
- [ ] No functions longer than 50 lines
- [ ] No file longer than 300 lines
- [ ] All features accessible through Gradio
- [ ] Zero hardcoded URLs or API keys
- [ ] Clean separation of concerns

## Example Gradio Interface Structure

```python
# This is what you're aiming for in the UI:
with gr.Blocks() as demo:
    gr.Markdown("# Pixel Sorter")
    
    with gr.Tab("Basic Options"):
        with gr.Row():
            input_image = gr.Image(type="pil")
            output_image = gr.Image(type="pil")
        
        with gr.Row():
            interval_dropdown = gr.Dropdown(
                choices=list(INTERVAL_FUNCTIONS.keys()),
                value="random",
                label="Interval Function"
            )
            sorting_dropdown = gr.Dropdown(
                choices=list(SORTING_FUNCTIONS.keys()),
                value="lightness",
                label="Sorting Function"
            )
    
    with gr.Tab("Advanced Options"):
        # Add sliders for all parameters
        
    process_btn = gr.Button("Sort Pixels")
```

This structure provides a clear path from the current monolithic design to a modern, maintainable application.