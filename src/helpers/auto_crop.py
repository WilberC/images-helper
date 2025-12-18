"""Automatic image cropping to remove blank borders"""
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np


def auto_crop(input_path: str, output_path: str, threshold: int = 10) -> None:
    """
    Automatically crop an image to remove blank/transparent borders.
    
    This function detects the bounding box of non-blank content and crops
    the image to that region, removing any unnecessary whitespace or 
    transparent areas around the edges.
    
    Args:
        input_path: Path to input image
        output_path: Path to save cropped image
        threshold: Pixel value threshold for detecting non-blank content (0-255).
                  Lower values are more aggressive. Default is 10.
    
    Raises:
        ValueError: If threshold is invalid
        IOError: If image cannot be read or written
    """
    if not 0 <= threshold <= 255:
        raise ValueError("Threshold must be between 0 and 255")
    
    # Open image
    img = Image.open(input_path)
    
    # Handle different image modes
    if img.mode == 'RGBA':
        # For images with transparency, use alpha channel
        bbox = _get_bbox_with_alpha(img, threshold)
    else:
        # For RGB/L images, detect based on color difference from background
        bbox = _get_bbox_without_alpha(img, threshold)
    
    if bbox is None:
        # Image is completely blank, save as is
        print("Warning: Image appears to be completely blank")
        img.save(output_path)
        return
    
    # Crop to bounding box
    cropped = img.crop(bbox)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save cropped image
    cropped.save(output_path)


def _get_bbox_with_alpha(img: Image.Image, threshold: int) -> tuple:
    """
    Get bounding box for images with alpha channel.
    
    Args:
        img: PIL Image with RGBA mode
        threshold: Alpha threshold value
        
    Returns:
        Bounding box as (left, top, right, bottom) or None if image is blank
    """
    # Get alpha channel
    alpha = img.split()[-1]
    
    # Convert to numpy for easier processing
    alpha_array = np.array(alpha)
    
    # Find rows and columns with non-transparent pixels
    rows = np.any(alpha_array > threshold, axis=1)
    cols = np.any(alpha_array > threshold, axis=0)
    
    if not rows.any() or not cols.any():
        return None
    
    # Get bounding box coordinates
    top = np.argmax(rows)
    bottom = len(rows) - np.argmax(rows[::-1])
    left = np.argmax(cols)
    right = len(cols) - np.argmax(cols[::-1])
    
    return (left, top, right, bottom)


def _get_bbox_without_alpha(img: Image.Image, threshold: int) -> tuple:
    """
    Get bounding box for images without alpha channel.
    
    This method assumes the background is at the edges and detects
    content by comparing pixels to the corner background color.
    
    Args:
        img: PIL Image without alpha channel
        threshold: Color difference threshold
        
    Returns:
        Bounding box as (left, top, right, bottom) or None if image is blank
    """
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get background color from corners (average of 4 corners)
    width, height = img.size
    corners = [
        img.getpixel((0, 0)),
        img.getpixel((width - 1, 0)),
        img.getpixel((0, height - 1)),
        img.getpixel((width - 1, height - 1))
    ]
    
    # Use most common corner color as background
    bg_color = max(set(corners), key=corners.count)
    
    # Create a background image with the detected color
    bg = Image.new('RGB', img.size, bg_color)
    
    # Get difference between image and background
    diff = ImageChops.difference(img, bg)
    
    # Convert to grayscale and apply threshold
    diff_gray = diff.convert('L')
    diff_array = np.array(diff_gray)
    
    # Find rows and columns with significant differences
    rows = np.any(diff_array > threshold, axis=1)
    cols = np.any(diff_array > threshold, axis=0)
    
    if not rows.any() or not cols.any():
        return None
    
    # Get bounding box coordinates
    top = np.argmax(rows)
    bottom = len(rows) - np.argmax(rows[::-1])
    left = np.argmax(cols)
    right = len(cols) - np.argmax(cols[::-1])
    
    return (left, top, right, bottom)
