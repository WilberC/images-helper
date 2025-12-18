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
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True
    
    # Resize command
    resize_parser = subparsers.add_parser('resize', help='Resize an image')
    resize_parser.add_argument('input', type=str, help='Input image path')
    resize_parser.add_argument('output', type=str, help='Output image path')
    resize_parser.add_argument('--width', type=int, required=True, help='Target width')
    resize_parser.add_argument('--height', type=int, required=True, help='Target height')
    resize_parser.add_argument('--keep-aspect', action='store_true', 
                              help='Maintain aspect ratio (fit within dimensions)')
    
    # Remove background command
    bg_parser = subparsers.add_parser('remove-bg', help='Remove image background')
    bg_parser.add_argument('input', type=str, help='Input image path')
    bg_parser.add_argument('output', type=str, help='Output image path')
    
    # Vectorize command
    vector_parser = subparsers.add_parser('vectorize', help='Convert image to vector (SVG)')
    vector_parser.add_argument('input', type=str, help='Input image path')
    vector_parser.add_argument('output', type=str, help='Output SVG path')
    vector_parser.add_argument('--colors', type=int, default=8, 
                              help='Number of colors to use (default: 8)')
    
    args = parser.parse_args()
    
    # Validate input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Route to appropriate handler
    try:
        if args.command == 'resize':
            resize_image(
                str(input_path),
                args.output,
                args.width,
                args.height,
                keep_aspect=args.keep_aspect
            )
            print(f"✓ Image resized successfully: {args.output}")
            
        elif args.command == 'remove-bg':
            remove_background(str(input_path), args.output)
            print(f"✓ Background removed successfully: {args.output}")
            
        elif args.command == 'vectorize':
            vectorize_image(str(input_path), args.output, colors=args.colors)
            print(f"✓ Image vectorized successfully: {args.output}")
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
