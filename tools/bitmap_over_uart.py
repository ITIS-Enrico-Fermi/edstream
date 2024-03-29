"""
Send bitmap over UART
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

SERIAL_PORT_NAME: str = "/dev/ttyUSB0"  # Default value

class BytePosition(IntEnum):
    """
    See send_start_byte docstring for more details
    """
    SAVE = 0
    ZIPPED = auto()
    SET_RR = auto()
    START = auto()
    CLEAR = auto()
    SIZE = auto()
    RESERVED_FOR_FUTURE_USE = auto()
    QUERY = auto()

class ProtocolHandler:
    def __init__(self, serial_port: serial.Serial) -> None:
        """
        Initializator
        :param serial.Serial serial_port: Open and active serial port over which send the data
        :return: Nothing
        :rtype: None
        """
        self.serial_port: serial.Serial = serial_port
    
    def __send_start_byte(self, clear: bool = False, start: bool = False, set_rr: bool = False, zipped: bool = False, save: bool = False, size_128x64: bool = False, query: bool = False) -> None:
        """
        Compose and send protocol's start byte. Parameters are sorted from the one with the highest priority to the one with the lowest priority
        :param bool clear: Clear embedded device's frame buffer. Highest priority, mutual exclusion. If it is equal to True no payload expected
        :param bool start: Start or stop animation on the embedded device. When equals to True the animation starts (no payload expected), otherwise the payload is added to the frame buffer
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
                | ((0x01 << int(BytePosition.START)) if start else 0x00) \
                | ((0x01 << int(BytePosition.SET_RR)) if set_rr else 0x00) \
                | ((0x01 << int(BytePosition.ZIPPED)) if zipped else 0x00) \
                | ((0x01 << int(BytePosition.SAVE)) if save else 0x00)
        start_byte: bytes = bytes([sb])
        # print(start_byte)
        self.serial_port.write(start_byte)

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

        has_ackd = (self.serial_port.read() == b'\xff')
        if not has_ackd:
            logging.warning("Device hasn't acknowledged")
        return has_ackd

    def send_bitmap(self, buf: bytes) -> None:
        """
        Send a series of bytes to the embedded device. Store these bytes and save them into the frame buffer
        :param bytes buf: bytes of which the bitmap image is made up of
        """
        self.__send_start_byte(zipped = False, save = True, size_128x64 = True)
        self.__check_ack()
        self.serial_port.write(buf)
        self.__check_ack()

    def set_refresh_rate(self, rr: int) -> None:
        """
        Set animation's refresh rate
        :param int rr: Refresh Rate value in milliseconds (later divided by portTICK_MS on the ESP32 MCU)
        """
        self.__send_start_byte(set_rr = True)
        self.__check_ack()
        self.serial_port.write(byte([rr]))
        self.__check_ack()

    def start(self) -> None:
        """
        Start animation
        """
        self.__send_start_byte(start = True)
        self.__check_ack()

    def clear(self) -> None:
        """
        Clear embedded device's frame buffer
        """
        self.__send_start_byte(clear = True)
        self.__check_ack()


def main(port: str, show: bool, start_animation: bool, refresh_rate: int, clear: bool, use_stdin: bool):
    with serial.Serial(port, baudrate=115200, bytesize=8) as uart:
        handler = ProtocolHandler(uart)
        if clear:
            handler.clear()
        elif start_animation:
            handler.start()
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
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default=SERIAL_PORT_NAME)
    parser.add_argument('-s', '--show', help='Show piped image (on the PC) before sending', default=False, action='store_true')
    parser.add_argument('--start-animation', help='Start animation on the target device. Inhibit default behavior (send bitmap). No piped image', default=False, action='store_true')
    parser.add_argument('--nostdin', help="Open image.bmp instead of stdin", default=True, action='store_false')

    parser.add_argument('--refresh-rate', help='Set animation refresh rate. Inhibit default behavior (send bitmap). No piped image', type=int, default=None)  # rr = None -> skip set_rr flag (false)
    
    parser.add_argument('--clear', help='Clear frame buffer stored on the embedded device. Inhibit default behavior (send bitmap). No piped image', default=False, action='store_true')
    args = parser.parse_args()
    main(args.port, args.show, args.start_animation, args.refresh_rate, args.clear, args.nostdin)

