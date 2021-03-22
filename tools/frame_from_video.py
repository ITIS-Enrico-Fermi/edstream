"""
Exract frame number f from video files and write it on stdout
"""

__authors__ = "5H wild nerds"

import sys
from io import BytesIO
import argparse
import cv2

def main(source: str, num: int) -> None:
    cap = cv2.VideoCapture(source)
    cap.set(cv2.CAP_PROP_POS_MSEC,(num*30))  # Go forward of 30 ms x frame number
    success, frame = cap.read()
    if success:
        en_success, en_buffer = cv2.imencode(".png", frame)
        sys.stdout.buffer.write(en_buffer.tobytes())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', help='Video source file', required=True, type=str)
    parser.add_argument('-f', '--frame', help='Frame number', required=True, type=int)

    args = parser.parse_args()

    main(args.source, args.frame)
