#include <stdio.h>
#include <string.h>

#include "driver/gpio.h"

#include "driver/i2c.h"
#include "ssd1306_hal/io.h"
#include "ssd1306.h"

#include "edstream.h"
#include "edstream_hal.h"

void app_main() {
    struct eds_hal_config eds_hal_conf = {
        .i2c = I2C_NUM_0,
        .sda_pin = 21,
        .scl_pin = 22
    };
    eds_hal_init(&eds_hal_conf);

    ssd1306_128x64_i2c_init();

    ssd1306_clearScreen();

    uint8_t cmd[512];
    int read;

    while(true) {
        read = eds_hal_recv(cmd, 512);
        eds_decode_message(cmd, read);
    }
}