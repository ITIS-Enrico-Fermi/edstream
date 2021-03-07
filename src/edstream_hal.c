/*
 *  EDStream HAL implementation
 *  (c) 2021 - Project EDStream
 * 
 *  ESP32 I2C_0 and UART_0
 */

#include "edstream_hal.h"

#include <stdio.h>
#include "ssd1306.h"

static struct eds_hal_config configuration;

void eds_hal_init(struct eds_hal_config *config) {
    configuration = *config;

    ssd1306_platform_i2cConfig_t cfg = {
        .sda = configuration.sda_pin,
        .scl = configuration.scl_pin
    };
    ssd1306_platform_i2cInit(configuration.i2c, 0, &cfg);

    //UART configuration is not handled at this time.
}

int eds_hal_send_byte(uint8_t x) {
    return putchar(x);
}

int eds_hal_send(uint8_t *src, int n) {
    return fwrite(src, sizeof(uint8_t), n, stdout);
}

int eds_hal_recv(uint8_t *dst, int n) {
    return fread(dst, sizeof(uint8_t), n, stdin);
}