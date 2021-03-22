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
    create_fifo(fifo_path)
    try:
        with serial.Serial(port=port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0) as uart, open(fifo_path, 'r+b', 0) as fifo:
            fd = fifo.fileno()
            os.set_blocking(fd, False)
            uart.flush()
            fifo_data: bytes = b''
            uart_data: bytes = b''
            uart_prev: bytes = b''
            while True:
                # r, w, x = select.select([fd], [fd], [])
                # logging.debug(f"r: {fd in r}, w: {fd in w}")
                # if fd in r:
                fifo_data = fifo.read()
                uart_data = uart.read()
                # if uart_data or fifo_data:
                #     logging.debug(f"UART: {uart_data}, FIFO: {fifo_data}, UART_PREV: {uart_prev}")

                # if fifo_data is None:  # Prevent echo between closed fifo and uart
                #     uart.flush()
                #     uart.flushOutput()
                #     uart_data = b''

                if uart_data == fifo_data or fifo_data == uart_prev:  # Prevent echo between closed fifo and uart
                    fifo_data = b''
                else:
                    uart_prev = uart_data

               # if uart_data == fifo_data or (uart_data == b'' and fifo_data == uart_data_last_val) or (fifo_data == b'' and uart_data == fifo_data_last_val):
               #     logging.debug(f"from UART: {uart_data}, from FIFO: {fifo_data}")
               #     uart_data = b''
               #     fifo_data = b''
               #     uart.flush()
               #     uart.flushInput()
               #     uart.flushOutput()

               # if uart_data:
               #     uart_data_last_val = uart_data
               # if fifo_data:
               #     fifo_data_last_val = fifo_data
                
                if uart_data:
                    logging.info(f"UART: {uart_data}")
                    fifo.write(uart_data)
                    # fifo.flush()
                                   
                if fifo_data:
                    # logging.info(f"FIFO: {len(fifo_data[-1024:])}")
                    uart.write(fifo_data[-1024:])
                    # uart.flush()
                
    except Exception as e:
        logging.debug(e)
        delete_fifo(fifo_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filemode="a", format="%(asctime)s - %(levelname)s -> %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default=SERIAL_PORT_NAME)
    parser.add_argument('-f', '--fifo', help='Named pipe (FIFO) for UART communication (debug_uart.py)', type=str, default='fifo')
    args = parser.parse_args()
    main(args.port, args.fifo)
