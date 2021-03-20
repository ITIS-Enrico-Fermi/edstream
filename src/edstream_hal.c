/*
 *  EDStream HAL implementation
 *  (c) 2021 - Project EDStream
 * 
 *  ESP32 I2C_0 and UART_0
 */

#include "edstream_hal.h"
#define LOG_LOCAL_LEVEL ESP_LOG_VERBOSE
#include "esp_log.h"

#include <stdio.h>
#include "ssd1306.h"

#include "driver/uart.h"

static struct eds_hal_config configuration;

static u8 uart_num_mem;
static QueueHandle_t queue_handle;

void eds_hal_init(const struct eds_hal_config *config) {

    configuration = *config;    

    // I2C
    ssd1306_platform_i2cConfig_t cfg = {
        .sda = config->i2c_pins.sda,
        .scl = config->i2c_pins.scl
    };
    ssd1306_platform_i2cInit(config->i2c_num, 0, &cfg);

    // UART
    ESP_ERROR_CHECK(uart_param_config(config->uart_num, &(config->uart_conf)));
    ESP_ERROR_CHECK(uart_set_pin(config->uart_num, config->uart_pins.tx, config->uart_pins.rx, config->uart_pins.rts, config->uart_pins.cts));
    ESP_ERROR_CHECK(uart_driver_install(config->uart_num, config->uart_buf_size, config->uart_buf_size, 10, &queue_handle, 0));
    uart_num_mem = config->uart_num;
}

int eds_hal_send_byte(u8 x) {
    return eds_hal_send(&x, 1);
}

int eds_hal_send(const u8 *src, u16 n) {
    size_t res = uart_write_bytes(uart_num_mem, (const char*) src, n);
    uart_wait_tx_done(uart_num_mem, 100);  // timeout of 100 ticks
    return res;
}

int eds_hal_recv(u8 *dst, int n) {
    return uart_read_bytes(UART_NUM_0, dst, n, 100 / portTICK_RATE_MS);
}

int eds_hal_display_show(const uint8_t *frame) {
    ssd1306_drawBuffer(0, 0, OLED_W, OLED_H, frame);
    return 0;
}