"""Image resizing functionality"""
from pathlib import Path
from PIL import Image
from src.utils import Spinner


def resize_image(input_path: str, output_path: str, width: int, height: int, 
                keep_aspect: bool = False) -> None:
    """
    Resize an image to specified dimensions.
    
    Args:
        input_path: Path to input image
        output_path: Path to save resized image
        width: Target width in pixels
        height: Target height in pixels
        keep_aspect: If True, maintain aspect ratio (fit within dimensions)
    
    Raises:
        ValueError: If dimensions are invalid
        IOError: If image cannot be read or written
    """
    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive integers")
    
    with Spinner("Resizing image..."):
        # Open image
        img = Image.open(input_path)
        
        if keep_aspect:
            # Calculate aspect ratio preserving dimensions
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            # Resize to exact dimensions
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save resized image
        img.save(output_path)
