#!/usr/bin/env python3
"""
Watermark removal using content-aware inpainting
"""
import cv2
import numpy as np
from PIL import Image


def remove_watermark(
    input_path: str,
    output_path: str,
    width_percent: int = 30,
    height_percent: int = 15,
    method: str = 'telea'
) -> None:
    """
    Remove watermark from the bottom-right corner of an image using inpainting.
    
    This function uses OpenCV's content-aware inpainting algorithms to intelligently
    fill in the watermarked region based on surrounding pixels.
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        width_percent: Percentage of image width to treat as watermark region (default: 30)
        height_percent: Percentage of image height to treat as watermark region (default: 15)
        method: Inpainting method - 'telea' (fast) or 'ns' (Navier-Stokes, higher quality)
    
    Raises:
        ValueError: If method is not 'telea' or 'ns'
        FileNotFoundError: If input file doesn't exist
    """
    # Validate method
    if method not in ['telea', 'ns']:
        raise ValueError("Method must be 'telea' or 'ns'")
    
    # Read image using OpenCV
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")
    
    # Get image dimensions
    height, width = img.shape[:2]
    
    # Calculate watermark region (bottom-right corner)
    watermark_width = int(width * (width_percent / 100))
    watermark_height = int(height * (height_percent / 100))
    
    # Create mask (white = area to inpaint, black = area to keep)
    mask = np.zeros((height, width), dtype=np.uint8)
    
    # Define the watermark region in bottom-right corner
    x_start = width - watermark_width
    y_start = height - watermark_height
    
    # Mark the watermark region in the mask
    mask[y_start:height, x_start:width] = 255
    
    # Choose inpainting algorithm
    if method == 'telea':
        inpaint_method = cv2.INPAINT_TELEA
    else:  # ns
        inpaint_method = cv2.INPAINT_NS
    
    # Perform inpainting
    # Radius determines how far the algorithm looks for reference pixels
    inpaint_radius = 3
    result = cv2.inpaint(img, mask, inpaint_radius, inpaint_method)
    
    # Convert BGR to RGB for PIL
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    
    # Save using PIL to maintain format compatibility
    output_img = Image.fromarray(result_rgb)
    output_img.save(output_path)


def remove_watermark_custom_region(
    input_path: str,
    output_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
    method: str = 'telea'
) -> None:
    """
    Remove watermark from a custom region of an image using inpainting.
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        x: X coordinate of top-left corner of watermark region
        y: Y coordinate of top-left corner of watermark region
        width: Width of watermark region in pixels
        height: Height of watermark region in pixels
        method: Inpainting method - 'telea' (fast) or 'ns' (Navier-Stokes, higher quality)
    
    Raises:
        ValueError: If method is not 'telea' or 'ns', or if region is invalid
        FileNotFoundError: If input file doesn't exist
    """
    # Validate method
    if method not in ['telea', 'ns']:
        raise ValueError("Method must be 'telea' or 'ns'")
    
    # Read image using OpenCV
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")
    
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Validate region
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError("Invalid region coordinates or dimensions")
    if x + width > img_width or y + height > img_height:
        raise ValueError("Region exceeds image boundaries")
    
    # Create mask
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    mask[y:y+height, x:x+width] = 255
    
    # Choose inpainting algorithm
    if method == 'telea':
        inpaint_method = cv2.INPAINT_TELEA
    else:  # ns
        inpaint_method = cv2.INPAINT_NS
    
    # Perform inpainting
    inpaint_radius = 3
    result = cv2.inpaint(img, mask, inpaint_radius, inpaint_method)
    
    # Convert BGR to RGB for PIL
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    
    # Save using PIL
    output_img = Image.fromarray(result_rgb)
    output_img.save(output_path)
