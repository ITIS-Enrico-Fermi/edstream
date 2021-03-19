/*
 *  EDStream HAL implementation
 *  (c) 2021 - Project EDStream
 * 
 *  ESP32 I2C_0 and UART_0
 */

#include "edstream_hal.h"

#include <stdio.h>
#include "ssd1306.h"

void eds_hal_init(const struct eds_hal_config *config)
{
    ssd1306_platform_i2cConfig_t cfg = {
        .sda = config->i2c_pins.sda_pin,
        .scl = config->i2c_pins.scl_pin
    };
    ssd1306_platform_i2cInit(config->i2c, 0, &cfg);

    //UART configuration is not handled at this time.
}

int eds_hal_send_byte(u8 x)
{
    return putchar(x);
}

int eds_hal_send(const u8 *src, u16 n)
{
    return fwrite(src, sizeof(uint8_t), n, stdout);
}

int eds_hal_recv(u8 *dst, u16 n)
{
    return fread(dst, sizeof(uint8_t), n, stdin);
}

int eds_hal_display_show(const u8 *frame)
{
    ssd1306_drawBitmap(0, 0, OLED_W, OLED_H, frame);
    return 0;
}