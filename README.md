# edstream
Bitmap streaming facility for ESP32 and OLED displays.

## Setting up

Clone this project into _lib_ folder inside your PIO workspace
```
cd lib
git clone https://github.com/ITIS-Enrico-Fermi/edstream
cd ..
```

Clone _ssd1306_ library into _components_ folder inside your PIO workspace
```
mkdir components && cd components
git clone https://github.com/lexus2k/ssd1306
cd ..
```

Copy PlatformIO configuration for a quick setup
```
cp lib/edstream/platformio.ini .
```

<<<<<<< HEAD
## Protocol

### Start byte
![Start byte](Protocol.svg)

### Send bitmap
![Send bitmap](SendBitmap.svg)

### Set refresh rate
![Set refresh rate](SetRefreshRate.svg)
<br> With _set_rr_ bit set to 1
<br> 1 byte payload expected

### Clear framebuffer
![Cleare framebuffer](Clear.svg)
<br> With _clear_ bit set to 1
<br> No payload expected

### Start animation
![Start animation](Start.svg)
<br> With _start_ bit set to 1
<br> No payload expected
=======
```
cp lib/edstream/sdkconfig .
```
For more information see: [https://github.com/lexus2k/ssd1306#setting-up]()
>>>>>>> 9ffc8311901d8c59a52382b625a764ccd0b5a919
