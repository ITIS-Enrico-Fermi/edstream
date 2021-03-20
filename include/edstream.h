#ifndef __EDSTREAM_H
#define __EDSTREAM_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "esp_log.h"
#include "edstream_hal.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

/*
 *  Protocol option bits
 */

//  Receiver should save this frame (as part of animation)
#define PROTOCOL_SAVE_FRAME         (0x01 << 0)
//  Sent frame is zipped
#define PROTOCOL_ZIPPED_FRAME       (0x01 << 1)

//  This msg. sets the refresh rate of the animation. Expected payload
//  is 1 byte with refresh rate in milliseconds (as uint8_t)
#define PROTOCOL_SET_FREQ           (0x01 << 2)

//  XOR function. If set starts/stops the animation. No payload is
//  expected
#define PROTOCOL_TOGGLE_ANIMATION   (0x01 << 3)

//  Clear animation buffer
#define PROTOCOL_CLEAR_BUF          (0x01 << 4)
#define PROTOCOL_SIZE               (0x01 << 5)

#define PROTOCOL_QUERY              (0x01 << 7)

#define QUERY_IS_ANIMATION_RUNNING  (0x01)
#define QUERY_SUPPORTED_FX          (0x02)
#define QUERY_BUFFER_SIZE           (0x03)

#define RESPONSE_ACK                (0xff)

#define FRAME_SIZE                  (1024)
#define MAX_FRAME_NUMBER            (5)

/*
 *  Controller functions
 */

int eds_send_frame(const u8 *frame, bool save, bool zip);
int eds_start_animation();
int eds_stop_animation();

bool eds_query_animation_status();

typedef void(*eds_zip_function_t)(u8 *src, u8 *dst, int *pl_size);
void eds_zip_function_set(eds_zip_function_t f);
void eds_zip_deflate(u8 *src, u8 *dst, int *pl_size);

/*
 *  Device functions
 */

//  Callback function to decode messages
int eds_decode_message(const u8 *payload, int i);

int eds_send_ack(void);
void eds_toggle_animation(void);
void eds_clear_framebuffer(void);

#endif //__EDSTREAM_H