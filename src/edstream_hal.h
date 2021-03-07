#ifndef __EDSTREAM_HAL
#define __EDSTREAM_HAL

#include "stdint.h"
#include "stdbool.h"

struct eds_hal_config {
    int     i2c;
    int     sda_pin;
    int     scl_pin;
    int     uart;
    int     tx_pin;
    int     rx_pin;
};
#define ESD_HAL_DEFAULT()   ((struct eds_hal_config){.i2c=0, .sda_pin=21, .scl_pin=22, .uart=0, .tx_pin=-1, .rx_pin=-1})

void eds_hal_init(struct eds_hal_config *config);

int eds_hal_send_byte(uint8_t x);

/*
 *  @return Number of sent bytes to UART
 */
int eds_hal_send(uint8_t *src, int n);

/*
 *  @return Number of read bytes from UART
 */
int eds_hal_recv(uint8_t *dst, int n);
int eds_hal_display_show(uint8_t *frame);

#endif