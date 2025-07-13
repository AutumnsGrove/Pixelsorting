# Dependency Analysis for Pixelsort.py

## Function-to-Dependency Mapping

### PIL/Pillow Dependencies
**Functions using PIL:**
- `ImgOpen()` - Uses `Image.open()`, `.convert()`, `.load()`
- `ElementaryCA()` - Uses `Image.new()`, `.putpixel()`, `.save()`
- `edge()` - Uses `.rotate()`, `.filter()`, `.convert()`, `.load()`
- `file_edges()` - Uses `.rotate()`, `.resize()`, `.filter()`, `.convert()`, `.load()`
- `file_mask()` - Uses `.resize()`
- `CropTo()` - Uses `.crop()`
- `snap_sort()` - Uses `Image.fromarray()`, `.save()`
- `shuffle_total()` - Uses `Image.fromarray()`, `.load()`
- `shuffled_axis()` - Uses `Image.fromarray()`, `.load()`
- `main()` - Uses `.rotate()`, `.save()`, `.show()`

**PIL Components Used:**
- `Image` module - Core image operations
- `ImageFilter.FIND_EDGES` - Edge detection filter
- Various methods: open, new, save, show, convert, rotate, resize, crop, filter, load, putpixel

### NumPy Dependencies
**Functions using NumPy:**
- `snap_sort()` - Uses `array()`, `mgrid`, `.reshape()`, `.take()`, choice from numpy.random
- `shuffle_total()` - Uses `array()`, shuffle from numpy.random
- `shuffled_axis()` - Uses `array()`, shuffle from numpy.random
- `ElementaryCA()` - Uses choice from numpy.random (when imported)

**NumPy Components Used:**
- `numpy.array()` - Array creation from images
- `numpy.mgrid` - Mesh grid generation for coordinate arrays
- `numpy.random.choice()` - Random sampling without replacement
- `numpy.random.shuffle()` - In-place array shuffling
- Array methods: `.reshape()`, `.take()`, `.shape`

### Requests Dependencies
**Functions using Requests:**
- `UploadImg()` - Uses `post()` for file uploads
- `ImgOpen()` - Uses `get()` with `stream=True` for image downloading
- `ReadPreset()` - Uses `get()` for API calls to fetch presets
- `main()` - Uses `request()` for database uploads (commented out)

**Requests Components Used:**
- `requests.get()` - HTTP GET requests for images and API data
- `requests.post()` - HTTP POST requests for uploads
- `requests.request()` - Generic HTTP requests
- Stream handling for large file downloads
- Exception handling: `ConnectionError`

### tqdm Dependencies
**Functions using tqdm:**
- `PixelAppend()` - Uses custom `ProgressBars()` lambda that wraps `trange()`
- `SortImage()` - Uses `ProgressBars()` for sorting progress
- `edge()` - Uses `ProgressBars()` and direct `tqdm()` with custom formatting
- `threshold()` - Uses `ProgressBars()`
- `random()` - Uses `ProgressBars()`
- `waves()` - Uses `ProgressBars()`
- `file_mask()` - Uses direct `tqdm()` and `ProgressBars()`
- `file_edges()` - Uses direct `tqdm()` and `ProgressBars()`
- `snap_sort()` - Uses `ProgressBars()`
- `shuffle_total()` - Uses `ProgressBars()`
- `shuffled_axis()` - Uses `ProgressBars()`
- `none()` - Uses `ProgressBars()`

**tqdm Components Used:**
- `tqdm()` - Basic progress bar with custom description formatting
- `trange()` - Range-based progress bar (wrapped in `ProgressBars` lambda)

### Standard Library Dependencies

#### argparse
**Functions using argparse:**
- `ArgParsing()` - Creates `ArgumentParser` instances, defines arguments
- `main()` - Uses `.parse_args()` to parse command line arguments

#### socket
**Functions using socket:**
- `HasInternet()` - Uses `socket.setdefaulttimeout()`, `socket.socket()`, `socket.AF_INET`, `socket.SOCK_STREAM`, `.connect()`

#### colorsys
**Functions using colorsys:**
- Lambda functions: `lightness`, `hue`, `saturation` - All use `rgb_to_hsv()`

#### datetime
**Functions using datetime:**
- `main()` - Uses `datetime.now().strftime()` for timestamp generation

#### json
**Functions using json:**
- `UploadImg()` - Uses `loads()` to parse API responses
- `ReadPreset()` - Uses `.json()` method on requests response
- `main()` - Uses `dumps()` for database payload (commented out)

#### os
**Functions using os:**
- `clear()` - Uses `os.name` and `os.system()`
- Lambda `RemoveOld` - Uses `os.path.exists()` and `os.remove()`

#### urllib.parse
**Functions using urllib.parse:**
- `ReadImageInput()` - Uses `urlparse()` to validate URLs

#### subprocess
**Functions using subprocess:**
- Package installation block - Uses `subprocess.run()` for pip installs

#### string
**Functions using string:**
- Lambda `IDGen` - Uses `ascii_lowercase`, `ascii_uppercase`, `digits`

#### random
**Functions using random:**
- Multiple functions use `rand.random()`, `rand.randint()`, `rand.choice()`, `rand.randrange()`, `rand.getrandbits()`

## Dependency Criticality Assessment

### Critical (Core Functionality)
- **PIL/Pillow** - Essential for all image operations, cannot be replaced
- **NumPy** - Required for array operations and specific effects (snap, shuffle)

### Important (Enhanced Features)
- **tqdm** - Provides user feedback but could be replaced with simpler progress indication
- **requests** - Needed for URL-based image input and API features

### Utility (Could be replaced)
- **argparse** - Could be replaced with click or other CLI libraries
- **colorsys** - Only used for color space conversion, could implement manually

### Standard Library (Built-in)
- All other dependencies are part of Python standard library

## Version Compatibility Notes

### Current Issues:
- No version pinning in original requirements.txt
- Some deprecated API endpoints (put.re service)
- Potential compatibility issues with newer PIL/NumPy versions

### Recommended Updates:
- Pin all dependency versions for reproducible builds
- Update to modern versions with security patches
- Replace deprecated argparse patterns with click
- Add type hints and use mypy for type checking
- Implement proper logging instead of print statements