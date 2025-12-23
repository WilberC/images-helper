"""Image vectorization functionality"""
from pathlib import Path
import subprocess
from PIL import Image
from src.utils import Spinner


def vectorize_image(input_path: str, output_path: str, colors: int = 8) -> None:
    """
    Convert a raster image to vector format (SVG).
    
    This function uses potrace for vectorization. The image is first converted
    to a format suitable for potrace processing.
    
    Args:
        input_path: Path to input image
        output_path: Path to save SVG output
        colors: Number of colors to use in vectorization (default: 8)
    
    Raises:
        ValueError: If colors parameter is invalid
        RuntimeError: If potrace is not installed or conversion fails
        IOError: If image cannot be read or written
    """
    if colors <= 0:
        raise ValueError("Number of colors must be positive")
    
    with Spinner("Vectorizing image..."):
        # Open and prepare image
        img = Image.open(input_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temporary bitmap for potrace
        temp_bmp = output_dir / f"temp_{Path(input_path).stem}.bmp"
        
        try:
            # Convert to grayscale and save as BMP for potrace
            img_gray = img.convert('L')
            img_gray.save(str(temp_bmp))
            
            # Run potrace to convert to SVG
            result = subprocess.run(
                ['potrace', str(temp_bmp), '-s', '-o', output_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if 'not found' in result.stderr or 'No such file' in result.stderr:
                    raise RuntimeError(
                        "potrace is not installed. Install it with: sudo apt-get install potrace"
                    )
                raise RuntimeError(f"Vectorization failed: {result.stderr}")
                
        finally:
            # Clean up temporary file
            if temp_bmp.exists():
                temp_bmp.unlink()
