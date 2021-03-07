#ifndef __EDSTREAM_H
#define __EDSTREAM_H

#include <stdint.h>
#include <stdbool.h>

/*
 *  Protocol option bits
 */

//  Receiver should save this frame (as part of animation)
#define PROTOCOL_SAVE_FRAME     (0x01 << 0)
//  Sent frame is zipped
#define PROTOCOL_ZIPPED_FRAME   (0x01 << 1)

//  This msg. sets the refresh rate of the animation. Expected payload
//  is 1 byte with refresh rate in milliseconds (as uint8_t)
#define PROTOCOL_SET_FREQ       (0x01 << 2)

//  XOR function. If set starts/stops the animation. No payload is
//  expected
#define PROTOCOL_TOGGLE_ANIMATION   (0x01 << 3)

//  Clear animation buffer
#define PROTOCOL_CLEAR_BUF      (0x01 << 4)

#define PROTOCOL_QUERY          (0x01 << 7)

#define QUERY_IS_ANIMATION_RUNNING  0x01
#define QUERY_SUPPORTED_FX          0x02
#define QUERY_BUFFER_SIZE           0x03

/*
 *  Controller functions
 */

int eds_send_frame(uint8_t *frame, bool save, bool zip);
int eds_start_animation();
int eds_stop_animation();

bool eds_query_animation_status();

typedef void(*eds_zip_function_t)(uint8_t *src, uint8_t *dst, int *pl_size);
void eds_zip_function_set(eds_zip_function_t f);
void eds_zip_deflate(uint8_t *src, uint8_t *dst, int *pl_size);
eds_zip_function_t eds_zip_function = eds_zip_deflate;

/*
 *  Device functions
 */

//  Callback function to decode messages
int eds_decode_message(uint8_t *payload, int i);

#endif //__EDSTREAM_H