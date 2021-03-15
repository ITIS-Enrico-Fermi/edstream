"""
Tool for UART debugging. Waits for a string on stdin representing the hex
dump of a bytes array.
The tool only writes on the serial port stream, a monitor should read the debug
response from the display controller (e.g. ESP32).
"""

__authors__ = "5H wild nerds"

import serial
import argparse

def send_raw_byte(port: serial.Serial, hex_repr: str):
    x = bytes.fromhex(hex_repr)
    port.write(x)

def main(port: str, speed: int):
    with serial.Serial(port, speed) as s:
        while True:
            payload = input(">> ")
            send_raw_byte(s, payload)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', default="/dev/cu.SLAB_USBtoUART")
    parser.add_argument('-b', '--baudrate', help='Serial port baudrate', type=int, default=115200)

    args = parser.parse_args()
    main(args.port, args.baudrate)