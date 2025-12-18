"""Background removal functionality"""
from pathlib import Path
from rembg import remove
from PIL import Image


def remove_background(input_path: str, output_path: str) -> None:
    """
    Remove background from an image.
    
    Args:
        input_path: Path to input image
        output_path: Path to save image with background removed
    
    Raises:
        IOError: If image cannot be read or written
    """
    # Open image
    img = Image.open(input_path)
    
    # Remove background
    output = remove(img)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save result
    output.save(output_path)
