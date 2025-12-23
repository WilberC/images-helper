"""Background removal functionality"""
from pathlib import Path
from PIL import Image
import numpy as np
from src.utils import Spinner


def detect_background_color(img: Image.Image) -> tuple:
    """
    Detect the background color by sampling corner pixels.
    
    Args:
        img: PIL Image object
    
    Returns:
        Tuple of RGB values representing the background color
    """
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Sample corners (top-left, top-right, bottom-left, bottom-right)
    width, height = img.size
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((width - 1, 0)),
        img.getpixel((0, height - 1)),
        img.getpixel((width - 1, height - 1))
    ]
    
    # Use the most common corner color as background
    # For simplicity, use the top-left corner
    return corners[0]


def remove_background(input_path: str, output_path: str, tolerance: int = 30) -> None:
    """
    Remove background color from an image.
    
    This function detects the background color (typically blank/white) from the
    corner pixels and removes only that specific color, preserving all other
    content in the image.
    
    Args:
        input_path: Path to input image
        output_path: Path to save image with background removed
        tolerance: Color difference tolerance (0-255). Higher values remove more
                   similar colors. Default is 30.
    
    Raises:
        IOError: If image cannot be read or written
    """
    with Spinner("Removing background..."):
        # Open image
        img = Image.open(input_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Detect background color
        bg_color = detect_background_color(img)
        
        # Convert image to numpy array for efficient processing
        data = np.array(img)
        
        # Separate RGB and alpha channels
        rgb = data[:, :, :3]
        alpha = data[:, :, 3] if data.shape[2] == 4 else np.ones(rgb.shape[:2], dtype=np.uint8) * 255
        
        # Calculate color difference from background
        bg_array = np.array(bg_color[:3])
        diff = np.sqrt(np.sum((rgb.astype(float) - bg_array) ** 2, axis=2))
        
        # Create mask: pixels similar to background become transparent
        mask = diff <= tolerance
        alpha[mask] = 0
        
        # Combine RGB with new alpha channel
        result = np.dstack((rgb, alpha))
        
        # Convert back to PIL Image
        output = Image.fromarray(result.astype(np.uint8), 'RGBA')
        
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save result
        output.save(output_path)
