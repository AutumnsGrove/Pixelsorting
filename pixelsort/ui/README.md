# Pixel Sorter UI Components

This directory contains the Gradio web interface for the pixel sorting application.

## Files

- `__init__.py` - Package initialization
- `gradio_interface.py` - Main Gradio interface implementation
- `progress_manager.py` - Progress tracking utilities for Gradio
- `README.md` - This documentation file

## Key Features

### Multi-Tab Interface
- **Basic Options**: Essential parameters for quick experimentation
- **Advanced Options**: Detailed threshold and interval parameters

### Function Support
- **10 Sorting Functions**: lightness, intensity, hue, saturation, red, green, blue, alpha, minimum, maximum
- **10 Interval Functions**: random, threshold, edges, waves, none, file, file-edges, snap, shuffle-total, shuffle-axis

### User Experience
- Example images for quick testing
- Real-time progress tracking with detailed steps
- Comprehensive parameter validation
- Clear status messages and error handling
- Responsive layout with side-by-side image comparison

### Progress Tracking
- Custom ProgressManager that translates processing steps to Gradio progress
- Six main processing steps with appropriate weights
- Detailed status messages for each operation

## Usage

### Launching the Interface

```python
from pixelsort.ui.gradio_interface import launch_interface

# Launch with default settings
launch_interface()

# Launch with custom settings
launch_interface(
    share=True,  # Create public link
    server_name="0.0.0.0",  # Allow external connections
    server_port=8080  # Custom port
)
```

### Using the Factory Function

```python
from pixelsort.ui.gradio_interface import create_interface

interface = create_interface()
interface.launch()
```

## Architecture

The interface is built using a modular approach:

1. **GradioInterface Class**: Main interface manager
2. **ProgressManager**: Handles progress tracking and reporting
3. **Integration Layer**: Connects to the PixelSorter processor from Phase 4

## Error Handling

- Configuration validation before processing
- Graceful error messages with emoji indicators
- Temporary file cleanup on both success and failure
- Original image returned on processing errors

## Development Notes

- All processing happens server-side for security
- Images are temporarily saved for processing then cleaned up
- Progress tracking uses weighted steps for accurate reporting
- Interface automatically discovers example images
- Supports all current sorting and interval functions