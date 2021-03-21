"""
daemon.py

MQTT bridge daemon for remote communication with edstream controller.
"""

__authors__ = "5H wild nerds"

import argparse
import logging
import paho.mqtt.client as mqtt
import serial
from queue import Queue
import threading
from bitmap_over_uart import ProtocolHandler
from io import BytesIO
from PIL import Image

class EdstreamMQTT(mqtt.Client):
    def __init__(self, frame_queue: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frame_queue = frame_queue

    def on_connect(self, mqttc, obj, flags, rc):
        logging.info(f"Connected to broker with return code {rc}")
        self.subscribe("edstream")

    def on_disconnect(self, mqttc, userdata, rc):
        if rc != 0:
            logging.warning(f"Unexpected disconnection from server. Result code {rc}")
        else:
            logging.info("Disconnected from broker")

    def on_message(self, mqttc, userdata, message: mqtt.MQTTMessage):
        logging.debug(f"Received message from topic {message.topic}")
        self.frame_queue.put(message.payload)


def main(port, broker_addr):
    with serial.Serial(port, baudrate=115200) as s:
        frame_queue = Queue()
        client = EdstreamMQTT(frame_queue, protocol=mqtt.MQTTv311)
        client.connect(broker_addr)
        phandler = ProtocolHandler(s)

        t = threading.Thread(target=client.loop_forever)
        t.start()

        s.flushInput()

        try:
            while True:
                frame = frame_queue.get()

                stdin_img_bytes = BytesIO(frame)
                img = Image.open(stdin_img_bytes)

                phandler.send_bitmap(img.tobytes())

                phandler.start()

        except KeyboardInterrupt:
            pass

        client.disconnect()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help='Serial port name', type=str, default="/dev/cu.SLAB_USBtoUART")
    parser.add_argument('-b', '--broker', help='Broker address', type=str, default="mqtt.ssh.edu.it")
    
    args = parser.parse_args()

    main(args.port, args.broker)