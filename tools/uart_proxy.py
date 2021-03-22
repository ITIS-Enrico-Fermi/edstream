"""
UART communication manager. Interface between the controller and the host device.
Run this script in background.
"""
import os
import serial
import logging
import argparse
import aiofiles
import asyncio
from typing import BinaryIO
from time import sleep
import select

__authors__ = "5h wild nerds"

SERIAL_PORT_NAME: str = "/dev/ttyUSB0"  # Default value

def create_fifo(path: str) -> None:
    if not os.path.exists(path):
        os.mkfifo(path)

def delete_fifo(path: str) -> None:
    os.unlink(path)

def main(port: str, fifo_path: str) -> None:
    create_fifo('fifo.in')
    create_fifo('fifo.out')
    try:
        with serial.Serial(port=port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0) as uart, open('fifo.in', 'rb', 0) as fifo_in, open('fifo.out', 'wb', 0) as fifo_out:
            fd_in = fifo_in.fileno()
            os.set_blocking(fd_in, False)
            uart.flushInput()
            uart.flushOutput()
            fifo_data: bytes = b''
            uart_data: bytes = b''
            while True:
                fifo_data = fifo_in.read(1024)
                uart_data = uart.read()
                
                if uart_data:
                    logging.info(f"UART: {uart_data}")
                    fifo_out.write(uart_data)
                    fifo_out.flush()

                if fifo_data:
                    logging.info(f"FIFO: {len(fifo_data)}")
                    uart.write(fifo_data)
                    uart.flush()
                
                
    except Exception as e:
        logging.debug(e)
        delete_fifo('fifo.in')
        delete_fifo('fifo.out')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filemode="a", format="%(asctime)s - %(levelname)s -> %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default=SERIAL_PORT_NAME)
    parser.add_argument('-f', '--fifo', help='Named pipe (FIFO) for UART communication (debug_uart.py)', type=str, default='fifo')
    args = parser.parse_args()
    main(args.port, args.fifo)
