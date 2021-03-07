"""
Convert images to bitmap, after some pre-processing (grayscale and resize)
Input: stdin - pipe the image into this script
Output: stdout - C-like array of bytes
"""

__authors__ = "5H wild nerds"

import sys
from io import BytesIO
from PIL import Image

def main() -> None:
    """
    Get input image as raw bytes
    """
    stdin_img_bytes: ByteIO = BytesIO(sys.stdin.buffer.read())
    
    """
    Processing
    """
    img: Image = Image.open(stdin_img_bytes)
    img: Image = img.convert('LA')  # Convert to grayscale
    img: Image = img.resize((128, 64), Image.LANCZOS)  # Resize to 128x64 or 128x62 [pixels]. Lanczos interpolation for best result
    
    """
    Saving image into ByteIO object
    """
    img_byte_array: BytesIO = BytesIO()
    img.save(img_byte_array, format = 'png')
    
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
