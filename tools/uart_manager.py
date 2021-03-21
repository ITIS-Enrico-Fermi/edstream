"""
UART communication manager. Interface between the controller and the host device.
Run this script in background.
"""
import os
import serial
import logging
import argparse
import asyncio
from typing import BinaryIO

__authors__ = "5h wild nerds"

SERIAL_PORT_NAME: str = "/dev/ttyUSB0"  # Default value

def create_fifo(path: str) -> None:
    if not os.path.exists(path):
        os.mkfifo(path)

def delete_fifo(path: str) -> None:
    os.unlink(path)

def read_fifo_coro(fifo: BinaryIO, uart: serial.Serial) -> None:
    fifo_data: bytes = fifo.read()
    print(fifo_data)
    if fifo_data:
        uart.write(fifo_data)
        logging.info(f"FIFO: {fifo_data}")

def read_uart_coro(fifo: BinaryIO, uart: serial.Serial) -> None:
    uart_data: bytes = uart.read()
    if uart_data:
        fifo.write(uart_data)
        logging.info(f"UART: {uart_data}")

async def main(port: str, fifo_path: str) -> None:
    create_fifo(fifo_path)
    try:
        with serial.Serial(port=port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0) as uart, open(fifo_path, 'r+b', 0) as fifo:
            fd = fifo.fileno()
            os.set_blocking(fd, False)
            uart.flush()
            loop = asyncio.get_event_loop()
            loop.add_reader(fifo, read_fifo_coro, fifo, uart)
            loop.add_reader(uart, read_uart_coro, fifo, uart)
            never = asyncio.Future()
            await never
    except:
        delete_fifo(fifo_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filemode="a", format="%(asctime)s - %(levelname)s -> %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default=SERIAL_PORT_NAME)
    parser.add_argument('-f', '--fifo', help='Named pipe (FIFO) for UART communication (debug_uart.py)', type=str, default='fifo')
    args = parser.parse_args()
    asyncio.run(main(args.port, args.fifo))