# Next Project - Shapes and Drawing Implementation Plan

## 🎯 Project Overview

This document outlines the implementation plan for adding two major features to the pixelsort application:

1. **Interactive Mask Drawing**: Allow users to draw exclusion zones on images with smooth drawing and automatic shape completion
2. **Geometric Segmentation**: Segment images into geometric shapes, process each independently, then reassemble

## 🏗️ Architecture Overview

### Feature 1: Mask-based Exclusion Drawing
- **Location**: Integrated into main Basic Options tab
- **Drawing Style**: Smooth, anti-aliased drawing with automatic shape completion
- **Shape Detection**: Auto-fill complete shapes (circles, rectangles, etc.) when detected
- **Real-time Preview**: Live mask overlay with visual feedback

### Feature 2: Geometric Segmentation & Reassembly  
- **Location**: New "Segmentation" tab
- **Supported Shapes**: Circle, hexagon, triangle, octagon, pentagon, square, diamond, plus custom SVG upload
- **Processing**: Parallel processing of segments with existing worker infrastructure
- **Performance**: Optimized for speed while supporting full-resolution images

## 📅 Session-by-Session Implementation

---

## Session 1: Core Mask Infrastructure
**Focus**: Backend mask handling and utilities

### Claude Code Instructions:
```markdown
I need to implement mask-based exclusion for my pixelsort project. Create the core infrastructure:

1. Add a new `pixelsort/utils/mask_utils.py` module with:
   - Functions to create, manipulate, and validate masks (numpy-based for performance)
   - Smooth drawing utilities with anti-aliasing
   - Shape detection algorithms (circle, rectangle detection using contour analysis)
   - Automatic shape completion when closed shapes are detected
   - Mask-to-image conversion utilities with proper alpha blending
   - Mask merging and boolean operations (union, intersection, difference)
   - Mask smoothing/feathering functions for seamless blending

2. Add a new `pixelsort/effects/mask_functions.py` module with:
   - Mask-aware interval functions that respect exclusion zones
   - Modified versions of existing interval functions (threshold, random, edges, waves, etc.) that skip masked pixels
   - Smart interval generation that works around masked areas
   - A registry system for mask-aware functions
   - Fallback behavior when masks cover entire intervals

3. Update `pixelsort/core/processor.py` to:
   - Accept optional mask parameter in PixelSorter constructor and all methods
   - Integrate mask checking in the pixel sorting pipeline before interval generation
   - Ensure masked pixels are perfectly preserved in output (no sorting applied)
   - Add mask validation and error handling
   - Support mask resizing when image scaling is applied

4. Add `pixelsort/utils/shape_detection.py`:
   - Algorithms to detect complete geometric shapes in user drawings
   - Circle detection using Hough circles
   - Rectangle/square detection using contour approximation
   - Polygon detection for triangles, hexagons, etc.
   - Shape completion functions that fill detected shapes

This is the foundation - no UI changes yet. Focus on solid, well-tested core functionality with numpy optimization.
```

---

## Session 2: Interactive Drawing Interface
**Focus**: Gradio drawing integration in main tab

### Claude Code Instructions:
```markdown
Add interactive mask drawing to the main Basic Options tab:

1. Update `pixelsort/ui/interface_components.py`:
   - Add mask drawing controls to the Basic Options tab (don't create new tab)
   - Add ImageEditor component with brush tools next to the main input image
   - Include brush size slider (1-50px), opacity slider, and drawing mode toggle
   - Add "Clear Mask", "Undo Last Stroke", and "Auto-Complete Shapes" buttons
   - Include real-time mask preview overlay on the input image
   - Add mask save/load functionality (JSON format for mask coordinates)

2. Update `pixelsort/ui/event_handlers.py`:
   - Event handlers for drawing interaction using Gradio's annotation features
   - Real-time mask preview updates as user draws
   - Shape detection and auto-completion triggers
   - Mask state management between draws and processing runs
   - Integration with existing image upload handlers

3. Update `pixelsort/ui/visualization_components.py`:
   - Real-time mask overlay visualization (semi-transparent red overlay)
   - Shape detection highlighting (green outline when complete shape detected)
   - Mask statistics display (percentage of image masked)
   - Before/after comparison showing masked vs unmasked areas

4. Enhance `pixelsort/ui/image_processor.py`:
   - Process images with mask data from Gradio annotations
   - Convert Gradio drawing data to mask arrays
   - Integrate with the mask utilities from Session 1
   - Handle mask scaling when image scaling is applied
   - Pass mask data through to the core processor

Integration with existing UI: Place drawing controls in a collapsible section within Basic Options tab, keeping the interface clean and organized.
```

---

## Session 3: Geometric Segmentation Framework  
**Focus**: Shape-based image segmentation backend

### Claude Code Instructions:
```markdown
Implement geometric image segmentation system:

1. Create `pixelsort/utils/shape_utils.py`:
   - Functions to generate geometric shapes: circle, hexagon, triangle, octagon, pentagon, square, diamond
   - Advanced shapes: star (5-pointed, 6-pointed), ellipse, rounded rectangle
   - Grid-based shape placement algorithms with customizable spacing and overlap
   - Shape rotation and scaling utilities
   - SVG path parser for custom shape upload support
   - Shape tessellation algorithms for efficient space coverage
   - Shape boundary smoothing and anti-aliasing

2. Create `pixelsort/utils/segmentation_utils.py`:
   - Image segmentation into shape-based regions with pixel-perfect boundaries
   - Segment extraction with proper edge handling and padding
   - Segment reconstruction utilities with seamless blending at boundaries
   - Coordinate mapping between segments and full image (forward and reverse)
   - Overlap region handling for smooth transitions
   - Memory-efficient segment processing (process one at a time for large images)
   - Segment validation and error recovery

3. Add `pixelsort/core/segmented_processor.py`:
   - SegmentedPixelSorter class that processes image segments independently
   - Integration with existing PixelSorter for individual segment processing
   - Parallel processing support using existing worker infrastructure
   - Segment reassembly with multiple blending modes (overlay, multiply, screen)
   - Progress tracking across all segments
   - Memory management for large images with many segments
   - Support for applying different pixelsort settings to different segments

4. Create `pixelsort/utils/custom_shapes.py`:
   - SVG path parser and rasterizer
   - Custom shape validation and optimization
   - Shape library management (save/load custom shapes)
   - Shape preview generation
   - Conversion between different shape formats

Focus on mathematical foundations, efficient algorithms, and robust error handling. Optimize for both speed and memory usage.
```

---

## Session 4: Segmentation UI Controls
**Focus**: User interface for segmentation features

### Claude Code Instructions:
```markdown
Add segmentation controls in a new dedicated tab:

1. Update `pixelsort/ui/interface_components.py`:
   - Create new "Segmentation" tab with comprehensive shape controls
   - Shape selection dropdown: Circle, Hexagon, Triangle, Octagon, Pentagon, Square, Diamond, Star-5, Star-6, Ellipse, Custom SVG
   - Grid controls: segment size slider (10-500px), spacing slider (0-100px), overlap slider (0-50%)
   - Shape parameters: rotation slider (0-360°), aspect ratio for ellipses
   - Custom shape upload area for SVG files
   - Preview window showing segmentation pattern overlay on input image
   - Processing mode toggle: "Normal Processing" vs "Segmented Processing"
   - Per-segment settings: different pixelsort parameters for different segment types
   - Export options: individual segments, reassembled result, blend modes

2. Enhance `pixelsort/ui/visualization_components.py`:
   - Real-time segmentation pattern preview with shape outlines
   - Interactive shape positioning (drag to adjust grid offset)
   - Shape overlay visualization on input image with different colors per segment
   - Before/after comparison gallery for segmented results
   - Segment statistics (count, average size, coverage percentage)
   - Custom shape preview when SVG is uploaded
   - Animation preview showing processing order

3. Update `pixelsort/ui/event_handlers.py`:
   - Connect all segmentation controls to real-time preview updates
   - Handle segmented vs normal processing mode switching
   - Custom shape upload and validation handling
   - Shape parameter change event handlers with debouncing for performance
   - Integration with main processing button to support segmented mode
   - Progress tracking for segmented processing with per-segment updates

4. Add `pixelsort/ui/segmentation_presets.py`:
   - Predefined segmentation configurations (honeycomb, geometric patterns, artistic layouts)
   - Preset save/load functionality specific to segmentation
   - Integration with existing preset system

Build intuitive controls that make complex segmentation accessible to users. Include plenty of visual feedback and real-time previews.
```

---

## Session 5: Advanced Features & Optimization
**Focus**: Enhanced functionality and performance

### Claude Code Instructions:
```markdown
Add advanced features and optimize performance:

1. Enhance mask functionality in `pixelsort/utils/advanced_mask_utils.py`:
   - Multiple mask layers with different exclusion types (soft exclude, hard exclude, invert effect)
   - Feathered mask edges with customizable falloff curves
   - Mask morphology operations (erode, dilate, open, close)
   - Mask animation support for creating dynamic exclusion zones
   - Gradient masks and procedural mask generation
   - Mask blending modes and opacity controls

2. Improve segmentation in `pixelsort/utils/advanced_segmentation.py`:
   - Adaptive segment sizing based on image content (edge detection, color variance)
   - Voronoi diagram segmentation for organic patterns
   - Content-aware segmentation using image analysis
   - Cross-segment processing effects (bleed effects, segment interaction)
   - Hierarchical segmentation (segments within segments)
   - Smart segment boundaries that follow image features

3. Add export/import features in `pixelsort/utils/project_manager.py`:
   - Save/load complete project configurations (masks + segmentation + parameters)
   - Export individual segments as separate images with metadata
   - Batch processing with saved configurations and queuing system
   - Project templates and sharing functionality
   - Configuration versioning and history

4. Performance optimizations in `pixelsort/utils/performance_optimizer.py`:
   - Intelligent caching for mask and segmentation computations
   - Memory pooling for large image processing
   - GPU acceleration support where available (optional)
   - Streaming processing for extremely large images
   - Background processing with proper cancellation support
   - Performance profiling and bottleneck identification

5. Add `pixelsort/ui/advanced_controls.py`:
   - Expert mode with advanced parameter exposure
   - Batch processing interface
   - Performance monitoring dashboard
   - Memory usage indicators and optimization suggestions

Focus on making the features production-ready with enterprise-level performance and reliability.
```

---

## Session 6: Integration & Polish
**Focus**: Final integration, testing, and user experience

### Claude Code Instructions:
```markdown
Complete integration, testing, and user experience polish:

1. Create comprehensive presets in `pixelsort/config/enhanced_presets.py`:
   - Showcase presets combining masks + segmentation + pixelsort effects
   - Artistic presets: "Honeycomb Dreams", "Geometric Explosion", "Selective Chaos"
   - Practical presets: "Background Only", "Subject Protection", "Edge Enhancement"
   - Update preset system to handle mask and segmentation parameters
   - Add preset thumbnails and descriptions with visual examples

2. Add comprehensive error handling in `pixelsort/utils/error_handling.py`:
   - Validate mask and segmentation parameters with helpful error messages
   - Graceful fallbacks for invalid configurations (auto-correction where possible)
   - User-friendly error messages with specific troubleshooting suggestions
   - Recovery mechanisms for partial failures in segmented processing
   - Input validation for custom shapes and drawing data

3. Performance testing and optimization in `pixelsort/tests/performance_tests.py`:
   - Benchmark suite for mask and segmentation features
   - Memory usage profiling with large images (up to 50MP)
   - Processing time optimization for various image sizes and segment counts
   - Stress testing with extreme configurations
   - Performance regression testing

4. Create comprehensive documentation:
   - Update all function docstrings with new parameters and examples
   - Add interactive help system in the UI with tooltips and guides
   - Create visual tutorials for mask drawing and segmentation
   - Add technical documentation for developers
   - Performance guidelines and best practices for users

5. User experience improvements in `pixelsort/ui/ux_enhancements.py`:
   - Undo/redo system for all operations
   - Keyboard shortcuts for common operations
   - Drag-and-drop support for shape files and presets
   - Smart defaults that adapt to image content
   - Contextual help and feature discovery
   - Accessibility improvements (screen reader support, keyboard navigation)

6. Quality assurance:
   - Integration tests covering all feature combinations
   - Edge case testing (empty masks, single-pixel segments, etc.)
   - Cross-platform compatibility testing
   - Memory leak detection and prevention
   - User acceptance testing scenarios

Ensure everything works together seamlessly and provides a polished, professional user experience.
```

---

## 🔧 Technical Implementation Details

### Key Integration Points
1. **Mask System**: 
   - Integrates at interval generation level in `effects/interval_functions.py`
   - Modifies pixel grouping to skip masked areas
   - Preserves original pixels in masked regions

2. **Segmentation**: 
   - Creates multiple mini-processing jobs that run in parallel
   - Uses existing worker infrastructure from `ui/progress_manager.py`
   - Reassembles results with intelligent blending

3. **UI State Management**:
   - Maintains drawing state across processing runs
   - Synchronizes segmentation previews with parameter changes
   - Handles undo/redo for both drawing and segmentation

### Performance Considerations
- **Large Images**: Utilize existing image scaling in basic options
- **Parallel Processing**: Leverage existing worker setup for segment processing
- **Memory Management**: Process segments individually to manage memory usage
- **Caching**: Cache segmentation patterns and mask computations

### Data Flow Architecture
```
Input Image → [Mask Application] → [Segmentation] → Parallel Segment Processing → Intelligent Reassembly → Output
     ↓              ↓                     ↓                        ↓                         ↓
UI Drawing → Mask Generation → Shape Tessellation → Worker Queue → Blending Engine → Result Display
```

### New File Structure
```
pixelsort/
├── utils/
│   ├── mask_utils.py              # Core mask operations
│   ├── shape_utils.py             # Geometric shape generation
│   ├── segmentation_utils.py      # Image segmentation logic
│   ├── shape_detection.py         # Auto-shape completion
│   ├── custom_shapes.py           # SVG and custom shape support
│   ├── advanced_mask_utils.py     # Advanced mask features
│   ├── advanced_segmentation.py   # Advanced segmentation
│   ├── project_manager.py         # Save/load projects
│   ├── performance_optimizer.py   # Performance optimizations
│   └── error_handling.py          # Enhanced error handling
├── effects/
│   └── mask_functions.py          # Mask-aware interval functions
├── core/
│   └── segmented_processor.py     # Segmented processing engine
├── config/
│   └── enhanced_presets.py        # New preset configurations
├── ui/
│   ├── advanced_controls.py       # Expert mode controls
│   ├── segmentation_presets.py    # Segmentation-specific presets
│   ├── ux_enhancements.py         # UX improvements
│   └── (existing files updated)
└── tests/
    └── performance_tests.py       # Performance benchmarks
```

## 🎯 Success Criteria

### Mask Drawing Feature
- [x] Smooth, responsive drawing with real-time preview
- [x] Automatic shape detection and completion
- [x] Integration with all existing pixelsort effects
- [x] Undo/redo functionality
- [x] Save/load mask configurations

### Segmentation Feature  
- [x] Support for 8+ geometric shapes plus custom SVG
- [x] Real-time segmentation preview
- [x] Parallel processing with progress tracking
- [x] Multiple blend modes for reassembly
- [x] Per-segment parameter customization

### Performance Requirements
- [x] Handle images up to 50MP efficiently
- [x] Real-time preview updates (< 100ms for UI feedback)
- [x] Memory usage scales linearly with image size
- [x] Parallel processing utilizes available CPU cores
- [x] Graceful degradation for resource-constrained systems

### User Experience
- [x] Intuitive interface requiring minimal learning
- [x] Comprehensive error handling with helpful messages
- [x] Extensive preset library showcasing capabilities
- [x] Visual tutorials and contextual help
- [x] Professional-grade output quality

---

*This document serves as the complete roadmap for implementing advanced mask drawing and geometric segmentation features in the pixelsort application. Each session builds upon the previous work, ensuring a robust and feature-rich final implementation.*