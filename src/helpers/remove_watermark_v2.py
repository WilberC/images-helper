#!/usr/bin/env python3
"""
Advanced watermark removal using LaMa (Large Mask Inpainting) ONNX model
Reimplementation of Gemini-Watermark-Remover in Python
"""
import os
import numpy as np
from PIL import Image
import onnxruntime as ort
from pathlib import Path
from typing import Tuple, Optional


class LamaWatermarkRemover:
    """
    LaMa-based watermark remover using ONNX runtime
    
    This class implements the same workflow as the Gemini-Watermark-Remover
    Chrome extension, but in Python for command-line usage.
    """
    
    # Model configuration
    MODEL_INPUT_SIZE = 512
    WATERMARK_HEIGHT_RATIO = 0.15  # 15% from bottom
    WATERMARK_WIDTH_RATIO = 0.15   # 15% from right
    EXTENDED_RATIO = 0.16          # Extended region for better blending
    
    def __init__(self, model_path: str):
        """
        Initialize the LaMa watermark remover
        
        Args:
            model_path: Path to the lama_fp32.onnx model file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Initialize ONNX Runtime session
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        
        # Get model input/output names
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_name = self.session.get_outputs()[0].name
        
    def calculate_watermark_region(
        self, 
        width: int, 
        height: int, 
        ratio: Optional[float] = None
    ) -> Tuple[int, int, int, int]:
        """
        Calculate watermark region coordinates (bottom-right corner)
        
        Args:
            width: Image width
            height: Image height
            ratio: Optional custom ratio (uses default if None)
            
        Returns:
            Tuple of (x, y, region_width, region_height)
        """
        height_ratio = ratio if ratio else self.WATERMARK_HEIGHT_RATIO
        width_ratio = ratio if ratio else self.WATERMARK_WIDTH_RATIO
        
        region_width = int(width * width_ratio)
        region_height = int(height * height_ratio)
        x = width - region_width
        y = height - region_height
        
        return x, y, region_width, region_height
    
    def preprocess_image(self, image: Image.Image) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess image for model input
        
        Converts image to model input size (512x512), normalizes to [0, 1],
        and creates a mask for the watermark region.
        
        Args:
            image: PIL Image to preprocess
            
        Returns:
            Tuple of (image_tensor, mask_tensor) in NCHW format
        """
        # Resize to model input size
        resized = image.resize(
            (self.MODEL_INPUT_SIZE, self.MODEL_INPUT_SIZE),
            Image.Resampling.LANCZOS
        )
        
        # Convert to RGB if needed
        if resized.mode != 'RGB':
            resized = resized.convert('RGB')
        
        # Convert to numpy array and normalize to [0, 1]
        img_array = np.array(resized).astype(np.float32) / 255.0
        
        # Convert HWC to CHW format
        img_array = np.transpose(img_array, (2, 0, 1))
        
        # Add batch dimension: (1, 3, H, W)
        image_tensor = np.expand_dims(img_array, axis=0)
        
        # Create mask tensor
        mask = np.zeros(
            (self.MODEL_INPUT_SIZE, self.MODEL_INPUT_SIZE),
            dtype=np.float32
        )
        
        # Calculate watermark region
        x, y, w, h = self.calculate_watermark_region(
            self.MODEL_INPUT_SIZE,
            self.MODEL_INPUT_SIZE
        )
        
        # Set mask: 1.0 for watermark region, 0.0 for rest
        mask[y:y+h, x:x+w] = 1.0
        
        # Add batch and channel dimensions: (1, 1, H, W)
        mask_tensor = np.expand_dims(np.expand_dims(mask, axis=0), axis=0)
        
        return image_tensor, mask_tensor
    
    def postprocess_output(
        self, 
        output_tensor: np.ndarray
    ) -> np.ndarray:
        """
        Postprocess model output to image array
        
        Args:
            output_tensor: Model output in NCHW format
            
        Returns:
            Image array in HWC format (uint8)
        """
        # Remove batch dimension
        output = output_tensor[0]
        
        # Convert CHW to HWC
        output = np.transpose(output, (1, 2, 0))
        
        # Auto-detect value range and denormalize if needed
        max_val = np.max(np.abs(output[:100, :100]))  # Sample check
        if max_val <= 2.0:  # Normalized [0, 1]
            output = output * 255.0
        
        # Clamp to [0, 255] and convert to uint8
        output = np.clip(output, 0, 255).astype(np.uint8)
        
        return output
    
    def compose_final_image(
        self,
        original_image: Image.Image,
        processed_array: np.ndarray
    ) -> Image.Image:
        """
        Compose final image by blending original and processed regions
        
        Only replaces the watermark region, keeping the rest pristine.
        
        Args:
            original_image: Original full-resolution image
            processed_array: Processed 512x512 image array (HWC, uint8)
            
        Returns:
            Final composed PIL Image
        """
        orig_width, orig_height = original_image.size
        
        # Create final canvas at original resolution
        final_image = original_image.copy()
        
        # Convert processed array to PIL Image
        processed_image = Image.fromarray(processed_array, mode='RGB')
        
        # Calculate watermark regions for both images
        orig_x, orig_y, orig_w, orig_h = self.calculate_watermark_region(
            orig_width,
            orig_height,
            self.EXTENDED_RATIO
        )
        
        proc_x, proc_y, proc_w, proc_h = self.calculate_watermark_region(
            self.MODEL_INPUT_SIZE,
            self.MODEL_INPUT_SIZE,
            self.EXTENDED_RATIO
        )
        
        # Extract watermark region from processed image
        watermark_region = processed_image.crop((proc_x, proc_y, proc_x + proc_w, proc_y + proc_h))
        
        # Resize to match original image's watermark region
        watermark_region_resized = watermark_region.resize(
            (orig_w, orig_h),
            Image.Resampling.LANCZOS
        )
        
        # Paste onto final image
        final_image.paste(watermark_region_resized, (orig_x, orig_y))
        
        return final_image
    
    def remove_watermark(
        self,
        input_path: str,
        output_path: str
    ) -> None:
        """
        Remove watermark from image using LaMa model
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
        """
        # Load original image
        original_image = Image.open(input_path)
        
        # Preprocess
        image_tensor, mask_tensor = self.preprocess_image(original_image)
        
        # Prepare inputs for ONNX model
        inputs = {
            self.input_names[0]: image_tensor,
            self.input_names[1]: mask_tensor
        }
        
        # Run inference
        outputs = self.session.run([self.output_name], inputs)
        output_tensor = outputs[0]
        
        # Postprocess
        processed_array = self.postprocess_output(output_tensor)
        
        # Compose final image
        final_image = self.compose_final_image(original_image, processed_array)
        
        # Save result
        final_image.save(output_path, quality=95)


def remove_watermark_v2(
    input_path: str,
    output_path: str,
    model_path: Optional[str] = None
) -> None:
    """
    Remove watermark using LaMa ONNX model (v2 implementation)
    
    This is a high-level wrapper function that uses the LaMa model
    for advanced watermark removal with AI-based inpainting.
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        model_path: Optional path to lama_fp32.onnx model
                   (defaults to assets/lama_fp32.onnx)
    
    Raises:
        FileNotFoundError: If input file or model file doesn't exist
    """
    # Default model path
    if model_path is None:
        # Assume model is in assets/lama_fp32.onnx relative to project root
        project_root = Path(__file__).parent.parent.parent
        model_path = str(project_root / 'assets' / 'lama_fp32.onnx')
    
    # Validate input file
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Create remover and process
    remover = LamaWatermarkRemover(model_path)
    remover.remove_watermark(input_path, output_path)
