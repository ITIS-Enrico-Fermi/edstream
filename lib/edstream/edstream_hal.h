#include "stdint.h"
#include "stdbool.h"

int eds_hal_send(uint8_t *src, int i);
int eds_hal_send_byte(uint8_t x);
int eds_hal_recv(uint8_t *dst, int i);
int eds_hal_display_show(uint8_t *frame);