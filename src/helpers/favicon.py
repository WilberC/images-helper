"""
Favicon generation helper

Converts images to favicon format (.ico) with multiple sizes.
"""
from PIL import Image
from pathlib import Path
from typing import List, Tuple
from src.utils import Spinner


def generate_favicon(
    input_path: str,
    output_path: str,
    sizes: List[int] = None
) -> None:
    """
    Generate a favicon (.ico) from an input image with multiple sizes.
    
    Args:
        input_path: Path to input image
        output_path: Path to save favicon (.ico file)
        sizes: List of sizes to include in the favicon (default: [16, 32, 48])
               Common sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If invalid sizes are provided
        IOError: If there's an error saving the favicon
    """
    # Default sizes for favicons
    if sizes is None:
        sizes = [16, 32, 48]
    
    # Validate sizes
    if not sizes:
        raise ValueError("At least one size must be specified")
    
    for size in sizes:
        if size <= 0 or size > 256:
            raise ValueError(f"Invalid size {size}. Sizes must be between 1 and 256 pixels")
    
    with Spinner("Generating favicon..."):
        # Load the input image
        try:
            img = Image.open(input_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Input file not found: {input_path}")
        except Exception as e:
            raise IOError(f"Error loading image: {str(e)}")
        
        # Convert to RGBA if not already (ICO format supports transparency)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create resized versions for each size
        icon_images = []
        for size in sorted(sizes):
            # Create a copy and resize
            resized = img.copy()
            resized.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # If the image doesn't fill the size (due to aspect ratio),
            # create a new image with transparent background
            if resized.size != (size, size):
                final_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                # Center the resized image
                offset = ((size - resized.size[0]) // 2, (size - resized.size[1]) // 2)
                final_img.paste(resized, offset)
                icon_images.append(final_img)
            else:
                icon_images.append(resized)
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure output has .ico extension
        output_path_obj = Path(output_path)
        if output_path_obj.suffix.lower() != '.ico':
            output_path = str(output_path_obj.with_suffix('.ico'))
        
        # Save as ICO file with multiple sizes
        try:
            icon_images[0].save(
                output_path,
                format='ICO',
                sizes=[(img.size[0], img.size[1]) for img in icon_images]
            )
        except Exception as e:
            raise IOError(f"Error saving favicon: {str(e)}")
