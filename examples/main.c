#include <stdio.h>
#include <string.h>

#include "driver/gpio.h"

#include "driver/i2c.h"
#include <ssd1306.h>

#include "edstream.h"
#include "edstream_hal.h"

#define LOG_LOCAL_LEVEL ESP_LOG_ERROR
#include "esp_log.h"

void receiver(void *pvParameters)
{
    struct eds_hal_config eds_hal_conf = eds_hal_default();
    eds_hal_init(&eds_hal_conf);

    ssd1306_128x64_i2c_init();

    ssd1306_clearScreen();

    u8 cmd[512];
    int read;

    while(true) {
        vTaskDelay(1);
        read = eds_hal_recv(cmd, 512);
        if (read <= 0) continue;
        ESP_LOGD("RX", "Read bytes: %d", read);
        eds_decode_message(cmd, read);
    }

    vTaskDelete(NULL);
}

void app_main()
{
    // esp_log_level_set("*", ESP_LOG_VERBOSE);
    xTaskCreate(receiver, "receiver", 8192, NULL, 0, NULL);  // Yep, this is a huge amount of memory
}