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
Send an image to the embedded device
```
cat image.png | python to_bitmap.py | python bitmap_over_uart.py -s
```

### Video sream