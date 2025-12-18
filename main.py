#!/usr/bin/env python3
"""
Image Helper CLI - Main entry point for image processing operations
"""
import argparse
import sys
from pathlib import Path

from src.helpers.resize import resize_image
from src.helpers.remove_background import remove_background
from src.helpers.vectorize import vectorize_image
from src.helpers.auto_crop import auto_crop


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Image Helper - Process images with various operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py resize input.jpg output.jpg --width 800 --height 600
  python main.py remove-bg input.png output.png
  python main.py vectorize input.jpg output.svg
  python main.py auto-crop input.png output.png
  
Note: Input files are read from files/input/ and output files are saved to files/output/
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize an image')
    resize_parser.add_argument('input', type=str, help='Input image filename (from files/input/)')
    resize_parser.add_argument('output', type=str, help='Output image filename (to files/output/)')
    resize_parser.add_argument('--width', type=int, required=True, help='Target width')
    resize_parser.add_argument('--height', type=int, required=True, help='Target height')
    resize_parser.add_argument('--keep-aspect', action='store_true', 
                              help='Maintain aspect ratio (fit within dimensions)')
    
    # Remove background command
    bg_parser = subparsers.add_parser('remove-bg', help='Remove image background')
    bg_parser.add_argument('input', type=str, help='Input image filename (from files/input/)')
    bg_parser.add_argument('output', type=str, help='Output image filename (to files/output/)')
    
    # Vectorize command
    vector_parser = subparsers.add_parser('vectorize', help='Convert image to vector (SVG)')
    vector_parser.add_argument('input', type=str, help='Input image filename (from files/input/)')
    vector_parser.add_argument('output', type=str, help='Output SVG filename (to files/output/)')
    vector_parser.add_argument('--colors', type=int, default=8, 
                              help='Number of colors to use (default: 8)')
    
    # Auto-crop command
    crop_parser = subparsers.add_parser('auto-crop', help='Automatically crop blank borders')
    crop_parser.add_argument('input', type=str, help='Input image filename (from files/input/)')
    crop_parser.add_argument('output', type=str, help='Output image filename (to files/output/)')
    crop_parser.add_argument('--threshold', type=int, default=10,
                            help='Pixel threshold for detecting content (0-255, default: 10)')
    
    args = parser.parse_args()
    
    # Define base directories
    input_dir = Path('files/input')
    output_dir = Path('files/output')
    
    # Resolve input and output paths
    input_path = input_dir / args.input
    output_path = output_dir / args.output
    
    # Validate input file exists
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Route to appropriate handler
    try:
        if args.command == 'resize':
            resize_image(
                str(input_path),
                str(output_path),
                args.width,
                args.height,
                keep_aspect=args.keep_aspect
            )
            print(f"✓ Image resized successfully: {output_path}")
            
        elif args.command == 'remove-bg':
            remove_background(str(input_path), str(output_path))
            print(f"✓ Background removed successfully: {output_path}")
            
        elif args.command == 'vectorize':
            vectorize_image(str(input_path), str(output_path), colors=args.colors)
            print(f"✓ Image vectorized successfully: {output_path}")
            
        elif args.command == 'auto-crop':
            auto_crop(str(input_path), str(output_path), threshold=args.threshold)
            print(f"✓ Image cropped successfully: {output_path}")
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
