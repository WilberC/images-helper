# Image Helper

A Python CLI tool for common image processing operations including resizing, background removal, and vectorization.

## Features

- **Resize**: Resize images to specific dimensions with optional aspect ratio preservation
- **Remove Background**: Automatically remove backgrounds from images
- **Vectorize**: Convert raster images to SVG vector format
- **Auto-Crop**: Automatically detect and remove blank borders from images
- **Favicon**: Generate multi-size favicon (.ico) files for websites

## Installation

1. Clone this repository
2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. For vectorization, install potrace:
```bash
# Ubuntu/Debian
sudo apt-get install potrace

# macOS
brew install potrace
```

## Usage

### Resize Image
```bash
python main.py resize input.jpg output.jpg --width 800 --height 600
python main.py resize input.jpg output.jpg --width 800 --height 600 --keep-aspect
```

### Remove Background
```bash
python main.py remove-bg input.png output.png
```

### Vectorize Image
```bash
python main.py vectorize input.jpg output.svg
python main.py vectorize input.jpg output.svg --colors 16
```

### Auto-Crop Image
```bash
# Automatically remove blank borders
python main.py auto-crop input.png output.png

# Adjust sensitivity (lower = more aggressive cropping)
python main.py auto-crop input.png output.png --threshold 5
```

### Generate Favicon
```bash
# Generate favicon with default sizes (16x16, 32x32, 48x48)
python main.py favicon logo.png favicon.ico

# Generate favicon with custom sizes
python main.py favicon logo.png favicon.ico --sizes 16 32 48 64 128 256

# Generate high-quality favicon for modern browsers
python main.py favicon logo.png favicon.ico --sizes 32 64 128
```

## Project Structure

```
images-helper/
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py
│   └── helpers/           # Image processing functions
│       ├── __init__.py
│       ├── resize.py
│       ├── remove_background.py
│       ├── vectorize.py
│       ├── auto_crop.py
│       └── favicon.py
├── requirements.txt
└── README.md
```

## Adding New Features

To add a new image processing function:

1. Create a new file in `src/helpers/` (e.g., `src/helpers/my_feature.py`)
2. Implement your function with a clear signature:
```python
def my_feature(input_path: str, output_path: str, **kwargs) -> None:
    """
    Description of what this does.
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        **kwargs: Additional parameters
    """
    # Your implementation
    pass
```

3. Export it in `src/helpers/__init__.py`:
```python
from .my_feature import my_feature

__all__ = [
    # ... existing exports
    'my_feature',
]
```

4. Add a command in `main.py`:
```python
# Import at top
from src.helpers.my_feature import my_feature

# Add parser in main()
feature_parser = subparsers.add_parser('my-feature', help='Description')
feature_parser.add_argument('input', type=str, help='Input image path')
feature_parser.add_argument('output', type=str, help='Output image path')
# Add any additional arguments

# Add handler in the routing section
elif args.command == 'my-feature':
    my_feature(str(input_path), args.output)
    print(f"✓ Feature applied successfully: {args.output}")
```

## License

MIT
