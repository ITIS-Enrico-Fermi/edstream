"""
Convert images to bitmap, after some pre-processing (grayscale and resize)
Input: stdin - pipe the image into this script
Output: stdout - C-like array of bytes
"""

__authors__ = "5H wild nerds"

import sys
from io import BytesIO
from PIL import Image

def processing(image: Image) -> Image:
    image = image.resize((128, 64), Image.LANCZOS)  # Resize to 128x64 or 128x62 [pixels]. Lanczos interpolation for best result
    image = image.convert('1')  # Convert to 1 bit black/white

    return image


def main():
    """
    Get input image as raw bytes
    """
    stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
    
    """
    Processing
    """
    img = Image.open(stdin_img_bytes)
    img = processing(img)
    
    """
    Saving image into ByteIO object
    """
    img_byte_array = BytesIO()
    img.save(img_byte_array, format='bmp')
    
    """
    Getting bytes (array of bytes)
    """
    stdout_img_bytes: bytes = img_byte_array.getvalue()

    """
    Writing the array of bytes to stdout
    """
    sys.stdout.buffer.write(stdout_img_bytes)

if __name__ == "__main__":
    main()
