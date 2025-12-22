"""Image processing helper functions"""

from .resize import resize_image
from .remove_background import remove_background
from .vectorize import vectorize_image
from .auto_crop import auto_crop
from .favicon import generate_favicon
from .remove_watermark import remove_watermark
from .remove_watermark_v2 import remove_watermark_v2

__all__ = [
    'resize_image',
    'remove_background',
    'vectorize_image',
    'auto_crop',
    'generate_favicon',
    'remove_watermark',
    'remove_watermark_v2',
]
