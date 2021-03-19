"""
Tool for UART debugging. Waits for a string on stdin representing the hex
dump of a bytes array.
The tool only writes on the serial port stream, a monitor should read the debug
response from the display controller (e.g. ESP32).
"""

__authors__ = "5H wild nerds"

import serial
import argparse
import threading
import logging

def send_raw_byte(port: serial.Serial, hex_repr: str):
    x = bytes.fromhex(hex_repr)
    port.write(x)

def speed_test(port: serial.Serial):
    port.write(bytes([0]))
    for x in range(256):
        port.write(x.to_bytes(1, 'little'))

def main(port: str, speed: int, speedtest):
    with serial.Serial(port, speed) as s:
        if speedtest:
            speed_test(s)

        while True:
            payload = input(">> ")
            send_raw_byte(s, payload)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', default="/dev/cu.SLAB_USBtoUART")
    parser.add_argument('-b', '--baudrate', help='Serial port baudrate', type=int, default=115200)
    parser.add_argument('-s', '--speedtest', help='Performs a speed test', default=False, action='store_true')
    parser.add_argument('-d', '--display', help='Print incoming bytes using a separate thread', default=False, action='store_true')

    args = parser.parse_args()
    main(args.port, args.baudrate, args.speedtest)