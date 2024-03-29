# tools
Collection of useful tools for computer to embedded-device communication

## Setting up
Install dependencies for Python tools
```
python3 -m pip install -r requirements.txt
```

## Usage

### Args
Show the helper with
```
python bitmap_over_uart.py -h
```

| short arg |             arg             | action                                                                                                   |
|:---------:|:---------------------------:|----------------------------------------------------------------------------------------------------------|
| -h        | --help                      | show help message and exit                                                                               |
| -p PORT   | --port PORT                 | Serial port name                                                                                         |
| -s        | --show                      | Show piped image (on the PC) before sending                                                              |
|           | --start-animation           | Start animation on the target device. Inhibit default behavior (send bitmap). No piped image             |
|           | --refresh-rate REFRESH_RATE | Set animation refresh rate. Inhibit default behavior (send bitmap). No piped image                       |
|           | --clear                     | Clear frame buffer stored on the embedded device. Inhibit default behavior (send bitmap). No piped image |

### Image
Run UART manager and leave it in backround
```
python3 uart_proxy.py -p YOUR_SERIAL_PORT
```
Send an image to the embedded device
```
cat image.png | python3 to_bitmap.py | python3 rotate_pixel.py | python3 bitmap_over_fifo.py
```
Send a video clip to the ed
```
chmod +x from_video.sh
./from_video.sh rick_astley.mp4 50 99
```

Show the image or the video clip with
```
python3 bitmap_over_fifo.py --toggle-animation
```
The same command can be used to stop the animation (hide the image) and clear the display

If needed, set your device serial port with -p option in `uart_proxy.py` script

### MQTT

Open `daemon.py` and attach it to the serial port. This must remain open during the entire time of connection.
```
python3 daemon.py -p /dev/ttyUSB0
```

Send an image through MQTT
```
cat image.png | python3 to_bitmap.py | python3 rotate_pixel.py | mosquitto_pub -h mqtt.ssh.edu.it -t edstream --stdin-file
```

### Video stream

WIP
