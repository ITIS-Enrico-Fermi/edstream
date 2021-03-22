"""
rotate_pixel.py script

Converts GLCD or standard horizontal bitmap images to SSD1306 format.
Each byte represents a vertical pixel. Least significant bit is the first row,
therefore a simple rotation of 90 degrees clockwise is needed which is a trivial
operation to perform using Pillow.

You can invoke this script in your shell pipeline, or use it as a standalone function.
"""

from PIL import Image
import argparse
import sys
from io import BytesIO

__authors__ = "5H wild nerds"

def GLCD_to_SSD1306(image: Image) -> Image:
    output = bytearray()

    for bn in range(8): #block number
        block: Image = image.crop((0, bn*8, 128, bn*8+8))
        rblock: Image = block.rotate(-90, expand=True)
        output += rblock.tobytes()

    reassembled: Image = Image.frombytes('1', (64, 128), bytes(output))
    return reassembled



def main(use_stdin: bool, image: str):
    if use_stdin:
        stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
        img = Image.open(stdin_img_bytes)
    else:
        img = Image.open(image)

    output = bytearray()

    for bn in range(8): #block number
        block: Image = image.crop((0, bn*8, 128, bn*8+8))
        rblock: Image = block.rotate(-90, expand=True)
        output += rblock.tobytes()

    reassembled: Image = Image.frombytes('1', (64, 128), bytes(output))
    return reassembled


def main(use_stdin: bool, image: str):
    if use_stdin:
        stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
        img = Image.open(stdin_img_bytes)
    else:
        img = Image.open(image)
        
    reassembled: Image = GLCD_to_SSD1306(img)
    
    img_byte_array = BytesIO()
    reassembled.save(img_byte_array, format='bmp')
    stdout_img_bytes: bytes = img_byte_array.getvalue()
    sys.stdout.buffer.write(stdout_img_bytes)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nostdin', default=True, action='store_false')
    parser.add_argument('-i', '--image', default=None, required=False, type=str)
    
    args = parser.parse_args()

    main(args.nostdin, args.image)