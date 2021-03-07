"""
Convert images to bitmap
Input: stdin (pipe the image into this script)
Output: stdout
"""

__authors__ = "5H wild nerds"

import sys
from io import BytesIO
from PIL import Image

def main() -> None:
    stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
    img = Image.open(stdin_img_bytes).convert('LA')  # Convert to grayscale
    img.show()

if __name__ == "__main__":
    main()
