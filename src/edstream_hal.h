#ifndef __EDSTREAM_HAL
#define __EDSTREAM_HAL

#include "stdint.h"
#include "stdbool.h"
#include <stdio.h>
#include "ssd1306.h"
#include "driver/uart.h"

#define OLED_W          (128)
#define OLED_H          (64)
#define UART_NUM        (UART_NUM_0)  // Connected to CP2102
#define UART_BUF_SIZE   (2048)

typedef uint8_t u8;
typedef uint16_t u16;

static struct _i2c_pins {
    u8 sda;
    u8 scl;
};

static struct _uart_pins {
    int tx;  // -1 is valid
    int rx;
    int rts;
    int cts;
};

struct eds_hal_config {
    u8 i2c_num;
    u8 uart_num;
    struct _i2c_pins i2c_pins;
    struct _uart_pins uart_pins;        
    uart_config_t uart_conf;
    u16 uart_buf_size;
};
#define eds_hal_default() ((struct eds_hal_config){ .i2c_num=0, \
                                                    .i2c_pins = {.sda=21, .scl=22}, \
                                                    .uart_conf = {.baud_rate=115200, .data_bits=UART_DATA_8_BITS, .parity=UART_PARITY_DISABLE, \
                                                    .stop_bits=UART_STOP_BITS_1, .flow_ctrl=UART_HW_FLOWCTRL_DISABLE, .rx_flow_ctrl_thresh=122}, \
                                                    .uart_num = UART_NUM, \
                                                    .uart_pins = {.tx=UART_PIN_NO_CHANGE, .rx=UART_PIN_NO_CHANGE, .rts=18, .cts=19}, \
                                                    .uart_buf_size = UART_BUF_SIZE \
                                                    })

void eds_hal_init(const struct eds_hal_config *config);

int eds_hal_send_byte(u8 x);

/*
 *  @return Number of sent bytes to UART
 */
int eds_hal_send(const u8 *src, u16 n);

/*
 *  @return Number of read bytes from UART
 */
int eds_hal_recv(u8 *dst, int n);
int eds_hal_display_show(const uint8_t *frame);

#endif