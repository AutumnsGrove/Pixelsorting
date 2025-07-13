# Pixelsort - Modern Pixel Sorting Application

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

A modern, modular pixel sorting application with a clean web interface built using Gradio. This is a complete refactor of the original pixel sorting concept, providing an intuitive way to create stunning glitch art effects.

## What is Pixel Sorting

Pixel sorting is a digital art technique that creates glitch-like effects by sorting pixels in an image based on various criteria such as brightness, color, or intensity. The results can range from subtle artistic enhancements to dramatic abstract transformations.

Have a look at [this post](http://satyarth.me/articles/pixel-sorting/) or [/r/pixelsorting](http://www.reddit.com/r/pixelsorting/top/) for inspiration.

All credit goes to [the original repo](https://github.com/satyarth/pixelsort) for the foundational algorithms. This version provides a modern, user-friendly interface and modular architecture.

## Installation

### Prerequisites

- [Python 3.8+](https://www.python.org/downloads/) 
- [uv](https://github.com/astral-sh/uv) for package management

### Quick Install

```bash
# Clone the repository
git clone https://github.com/wolfembers/Pixelsorting.git
cd Pixelsorting

# Install dependencies using uv
uv pip install -r requirements.txt

# Alternative: Install the package directly
uv pip install -e .
```

### Development Install

For development with all testing dependencies:

```bash
uv pip install -r requirements.txt
uv pip install pytest mypy black
```

## Usage

### Web Interface (Recommended)

Launch the Gradio web interface for the easiest experience:

```bash
python -m pixelsort.main
```

Or directly:

```bash
python pixelsort/main.py
```

This will start a local web server (usually at `http://127.0.0.1:7860`) where you can:

- Upload images or provide image URLs
- Adjust sorting and interval parameters in real-time
- Preview results instantly
- Download processed images
- Experiment with different presets

### Gradio Interface Features

- **Image Input**: Upload local files or provide image URLs
- **Real-time Preview**: See results as you adjust parameters  
- **Parameter Controls**:
  - **Interval Function**: How to divide the image for sorting (`random`, `threshold`, `edges`, `waves`, `none`)
  - **Sorting Function**: How to order pixels (`lightness`, `intensity`, `hue`, `saturation`, `red`, `green`, `blue`)
  - **Thresholds**: Control sorting boundaries (0.0 - 1.0)
  - **Randomness**: Percentage of intervals to leave unsorted (0-100%)
  - **Angle**: Rotation angle for sorting direction (0-360°)
  - **Characteristic Length**: Controls interval sizes for certain functions
- **Preset System**: Quick access to popular configurations
- **Download**: Save results in PNG format

## Configuration Options

### Interval Functions

| Function | Description |
|----------|-------------|
| `random` | Randomly generate intervals with configurable lengths |
| `threshold` | Sort only pixels within lightness thresholds |
| `edges` | Use edge detection to define sorting boundaries |
| `waves` | Create wave-like intervals of uniform width |
| `none` | Sort entire rows without breaks |

### Sorting Functions

| Function | Description |
|----------|-------------|
| `lightness` | Sort by HSV lightness value |
| `intensity` | Sort by sum of RGB values |
| `hue` | Sort by HSV hue component |
| `saturation` | Sort by HSV saturation |
| `red` | Sort by red channel value |
| `green` | Sort by green channel value |
| `blue` | Sort by blue channel value |

### Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| Bottom Threshold | 0.0 - 1.0 | Lower boundary for threshold-based sorting |
| Upper Threshold | 0.0 - 1.0 | Upper boundary for threshold-based sorting |
| Randomness | 0 - 100% | Percentage of intervals to skip sorting |
| Angle | 0 - 360° | Rotation angle for sorting direction |
| Characteristic Length | 1+ | Average interval size for random intervals |

## Example Outputs

*All examples created using the web interface with different preset configurations.*

### Classic Glitch Effect
- **Interval Function**: `threshold`
- **Sorting Function**: `lightness` 
- **Result**: Creates the classic Kim Asendorf-style pixel sorting effect

### Abstract Waves  
- **Interval Function**: `waves`
- **Sorting Function**: `hue`
- **Result**: Flowing, wave-like color transitions

### Chaotic Random
- **Interval Function**: `random`
- **Sorting Function**: `intensity`
- **Randomness**: 50%
- **Result**: Balanced chaos with preserved image areas

## Tips and Tricks

- **Classic Effect**: Use `threshold` interval function with `lightness` sorting for the original pixel sorting look
- **Preserve Details**: Increase randomness to 30-70% to maintain recognizable image features
- **Color Focus**: Use hue or saturation sorting with edge-based intervals for artistic color effects
- **Experiment**: The web interface makes it easy to try different combinations in real-time

## Project Structure

```
pixelsort/
├── core/           # Main processing engine
├── effects/        # Sorting and interval functions  
├── ui/            # Gradio web interface
├── utils/         # Utilities and configuration
├── config/        # Configuration and presets
└── main.py        # Application entry point
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=pixelsort
```

### Code Quality

```bash
# Format code
black pixelsort/ tests/

# Type checking  
mypy pixelsort/
```

## Dependencies

The application uses modern Python packages:

- **PIL (Pillow)**: Image processing
- **Gradio**: Web interface
- **NumPy**: Numerical operations  
- **tqdm**: Progress bars
- **requests**: HTTP requests for remote images

See `requirements.txt` for complete dependency list with versions.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project builds upon the original pixel sorting work and is shared under the same spirit of open collaboration. See LICENSE for details.

## Acknowledgments

- Original pixel sorting algorithm by [Kim Asendorf](https://github.com/kimasendorf/ASDFPixelSort)
- Python implementation inspiration from [satyarth](https://github.com/satyarth/pixelsort)
- Modern refactor and web interface by the community