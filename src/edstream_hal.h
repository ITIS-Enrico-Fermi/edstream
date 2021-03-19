#ifndef __EDSTREAM_HAL
#define __EDSTREAM_HAL

#include "stdint.h"
#include "stdbool.h"

#define OLED_W  (128)
#define OLED_H  (64)

typedef uint8_t u8;
typedef uint16_t u16;

static struct _i2c_pins {
    u8 sda_pin;
    u8 scl_pin;
};

static struct _uart_pins {
    u8 tx_pin;
    u8 rx_pin;
};

struct eds_hal_config {
    union {  // Anonymous union
        u8 i2c;
        u8 uart;
    };
    union {
        struct _i2c_pins i2c_pins;
        struct _uart_pins uart_pins;        
    };
};
#define eds_hal_default() ((struct eds_hal_config){.i2c=0, .i2c_pins = {.sda_pin=21, .scl_pin=22}})

void eds_hal_init(const struct eds_hal_config *config);

int eds_hal_send_byte(u8 x);

/*
 *  @return Number of sent bytes to UART
 */
int eds_hal_send(const u8 *src, u16 n);

/*
 *  @return Number of read bytes from UART
 */
int eds_hal_recv(u8 *dst, u16 n);
int eds_hal_display_show(const uint8_t *frame);

#endif