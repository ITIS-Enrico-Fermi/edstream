/*
 *  EDStream HAL implementation
 *  (c) 2021 - Project EDStream
 * 
 *  ESP32 I2C_0 and UART_0
 */

#include "edstream_hal.h"

#include <stdio.h>
#include "ssd1306.h"

#include "driver/uart.h"

static struct eds_hal_config configuration;

void eds_hal_init(struct eds_hal_config *config) {
    configuration = *config;

    ssd1306_platform_i2cConfig_t cfg = {
        .sda = configuration.sda_pin,
        .scl = configuration.scl_pin
    };
    ssd1306_platform_i2cInit(configuration.i2c, 0, &cfg);

    //Reopen UART in blocking I/O mode
    QueueHandle_t uart_event_queue;
    ESP_ERROR_CHECK(uart_driver_install(UART_NUM_0, 2048, 2048, 10, &uart_event_queue, 0));

}

int eds_hal_send_byte(uint8_t x) {
    return putchar(x);
}

int eds_hal_send(uint8_t *src, int n) {
    return fwrite(src, sizeof(uint8_t), n, stdout);
}

int eds_hal_recv(uint8_t *dst, int n) {
    return uart_read_bytes(UART_NUM_0, dst, n, 100 / portTICK_RATE_MS);
}

int eds_hal_display_show(uint8_t *frame) {
    ssd1306_drawBitmap(0, 0, 128, 64, frame);
    return 0;
}