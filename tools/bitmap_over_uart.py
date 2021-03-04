import serial
import sys
import argparse
from io import BytesIO
from PIL import Image

SERIAL_PORT_NAME = "/dev/ttyUSB0"  # Default value

class ProtocolHandler:
    def __init__(self, serial_port: serial.Serial) -> None:
        """
        Initializator
        :param serial.Serial serial_port: Open and active serial port over which send the data
        :return: Nothing
        :rtype: None
        """
        self.serial_port: serial.Serial = serial_port
    
    def send_start_byte(self, clear: bool = False, ) -> None:
        """
        Compose and send protocol's start byte. Parameters are sorted from the one with the highest priority to the one with the lowest priority
        :param bool clear: Clear embedded device's frame buffer. Highest priority, mutual exclusion. If it is equal to True no payload expected
        :param bool start: Start or stop animation on the embedded device. When equals to True the animation starts (no payload expected, but you can set refresh-rate), otherwise the payload is added to the frame buffer
        :param bool set_rr: Set refresh-rate. Mutual exclusion. If equals to True 1 byte of payload expected; the payload must represent the refresh rate as ms(/portTICK_MS)
        :param bool zipped: 
        :param bool save:
        """

    def send_stop_byte(self) -> None:
        pass

    def send_bytes(self) -> None:
        pass

    def get_bytes(self) -> None:
        pass

    def check_ack(self) -> bool:
        pass

    def send(self) -> None:
        if not self.serial_port.is_open:
            exit(1)
        pass


def main(serial_port_name: str, show: bool) -> None:
    stdin_img_bytes = BytesIO(sys.stdin.buffer.read())
    if show:
        im = Image.open(stdin_img_bytes)
        im.show()
    with serial.Serial(port=serial_port_name, baudrate=115200, bytesize=8, parity='N', stopbits=1) as serial_port:
        handler: ProtocolHandler = ProtocolHandler(serial_port)
        handler.send(stdin_img_bytes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default=SERIAL_PORT_NAME)
    parser.add_argument('-s', '--show', help='Show piped image', default=False, action='store_true')
    args = parser.parse_args()
    main(args.port, args.show)

