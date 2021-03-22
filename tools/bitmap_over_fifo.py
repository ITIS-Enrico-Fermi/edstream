"""
Send bitmap over UART (through uart_manager.py)
"""

__authors__ = "5H wild nerds"

import serial
import sys
import argparse
from io import BytesIO
from PIL import Image
from enum import IntEnum, auto
from time import sleep
import logging
from typing import BinaryIO
import os
import time

class BytePosition(IntEnum):
    """
    See send_start_byte docstring for more details
    """
    SAVE = 0
    ZIPPED = auto()
    SET_RR = auto()
    TOGGLE = auto()
    CLEAR = auto()
    SIZE = auto()
    RESERVED_FOR_FUTURE_USE = auto()
    QUERY = auto()

class ProtocolHandler:
    def __init__(self, fifo_in: BinaryIO, fifo_out: BinaryIO) -> None:
        """
        Initializator
        :param BinaryIO fifo: Open fifo over which send and read the data
        :return: Nothing
        :rtype: None
        """
        self.fifo_in: BinaryIO = fifo_in
        self.fifo_out: BinaryIO = fifo_out
    
    def __send_start_byte(self, clear: bool = False, toggle: bool = False, set_rr: bool = False, zipped: bool = False, save: bool = False, size_128x64: bool = False, query: bool = False) -> None:
        """
        Compose and send protocol's start byte. Parameters are sorted from the one with the highest priority to the one with the lowest priority
        :param bool clear: Clear embedded device's frame buffer. Highest priority, mutual exclusion. If it is equal to True no payload expected
        :param bool toggle: Start and stop (toggle) animation on the embedded device. When equals to True the animation is toggled (no payload expected), otherwise the payload is added to the frame buffer
        :param bool set_rr: Set refresh-rate. Mutual exclusion. If equals to True 1 byte of payload expected; the payload must represent the refresh rate as ms(/portTICK_MS)
        :param bool zipped: If True the embedded device will unzip the frame
        :param bool save: Does the frame belong to an animation? If True the frame is saved in the frame buffer, otherwise is displayed immediately
        :param bool size_128x64: Set frame size. True => 128x64. False => 128x32
        :param bool query: Communicate to the embedded device if the master (PC) is writing or reading a frame
        """
        sb: int = 0x00 \
                | ((0x01 << int(BytePosition.QUERY)) if query else 0x00) \
                | ((0x01 << int(BytePosition.SIZE)) if size_128x64 else 0x00) \
                | ((0x01 << int(BytePosition.CLEAR)) if clear else 0x00) \
                | ((0x01 << int(BytePosition.TOGGLE)) if toggle else 0x00) \
                | ((0x01 << int(BytePosition.SET_RR)) if set_rr else 0x00) \
                | ((0x01 << int(BytePosition.ZIPPED)) if zipped else 0x00) \
                | ((0x01 << int(BytePosition.SAVE)) if save else 0x00)
        start_byte: bytes = bytes([sb])
        # print(start_byte)
        self.fifo_out.write(start_byte)
        self.fifo_out.flush()

    # def __send_stop_byte(self) -> None:
    #     """
    #     Send protocol's stop byte: 0x00
    #     """
    #     self.serial_port.write(bytes(0x00))

    def __check_ack(self) -> bool:
        """
        Check if the embedded device acknowledged start or stop byte
        ACK byte: 0xff
        """
        has_ackd = (self.fifo_in.read(1)  == b'\xff')
        if not has_ackd:
            logging.warning("Device hasn't acknowledged")
        return has_ackd

    def send_bitmap(self, buf: bytes) -> None:
        """
        Send a series of bytes to the embedded device. Store these bytes and save them into the frame buffer
        :param bytes buf: bytes of which the bitmap image is made up of
        """
        self.__send_start_byte(zipped = False, save = True, size_128x64 = True)
        assert self.__check_ack()
        # self.fifo_out.write(bytes(10))  # Wake up fifo.read() in uart_manager
        self.fifo_out.write(buf)  # buf's length must be 1024 bytes
        self.fifo_out.flush()
        assert self.__check_ack()

    def set_refresh_rate(self, rr: int) -> None:
        """
        Set animation's refresh rate
        :param int rr: Refresh Rate value in milliseconds (later divided by portTICK_MS on the ESP32 MCU)
        """
        self.__send_start_byte(set_rr = True)
        assert self.__check_ack()
        self.fifo_out.write(bytes([rr]))
        self.fifo_out.flush()
        assert self.__check_ack()

    def toggle(self) -> None:
        """
        Toggle animation
        """
        self.__send_start_byte(toggle = True)
        assert self.__check_ack() 

    def clear(self) -> None:
        """
        Clear embedded device's frame buffer
        """
        self.__send_start_byte(clear = True)
        self.__check_ack()


def main(fifo_path: str, show: bool, toggle_animation: bool, stop_animation: bool, refresh_rate: int, clear: bool, use_stdin: bool):
    with open('fifo.in', 'wb', 0) as fifo_out, open('fifo.out', 'rb', 0) as fifo_in:
        fd_in = fifo_in.fileno()
        os.set_blocking(fd_in, True)

        handler = ProtocolHandler(fifo_in, fifo_out)
        if clear:
            handler.clear()
        elif toggle_animation:
            handler.toggle()
        elif refresh_rate:
            handler.set_refresh_rate(refresh_rate)
        else:
            if use_stdin:
                stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
            img = Image.open(stdin_img_bytes if use_stdin else "lib/edstream/tools/image.bmp")

            if show:  # Show preview
                scaling_factor = 5
                w: int = img.size[0] * scaling_factor
                h: int = img.size[1] * scaling_factor
                img.resize((w, h), Image.ANTIALIAS).show()

            handler.send_bitmap(img.tobytes())
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fifo', help='Named pipe (FIFO) path', type=str, default='fifo')
    parser.add_argument('-s', '--show', help='Show piped image (on the PC) before sending', default=False, action='store_true')
    parser.add_argument('--toggle-animation', help='Start animation on the target device. Inhibit default behavior (send bitmap). No piped image', default=False, action='store_true')
    parser.add_argument('--stop-animation', help='Stop animation on the target device. Inhibit default behavior (send bitmap). No piped image', default=False, action='store_true')
    parser.add_argument('--nostdin', help="Open image.bmp instead of stdin", default=True, action='store_false')

    parser.add_argument('--refresh-rate', help='Set animation refresh rate. Inhibit default behavior (send bitmap). No piped image', type=int, default=None)  # rr = None -> skip set_rr flag (false)
    
    parser.add_argument('--clear', help='Clear frame buffer stored on the embedded device. Inhibit default behavior (send bitmap). No piped image', default=False, action='store_true')
    args = parser.parse_args()
    main(args.fifo, args.show, args.toggle_animation, args.stop_animation, args.refresh_rate, args.clear, args.nostdin)

