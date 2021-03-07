#include <string.h>

#include "edstream.h"
#include "edstream_hal.h"

static bool is_animation_running = false;
static eds_zip_function_t eds_zip_function = eds_zip_deflate;

/*
 *  @brief Sends a frame to display device (that controls the display)
 * 
 *  @param frame    1024 byte array representing a 128x64 frame
 *  @param save     True if device should save the frame
 *  @param zip      True if the frame should be zipped before sending
 * 
 *  You can provide a Deflate function with eds_zip_function_set()
 */
int eds_send_frame(uint8_t *frame, bool save, bool zip) {
    uint8_t message[1025];
    message[0] =
        save    ? PROTOCOL_SAVE_FRAME   : 0 |
        zip     ? PROTOCOL_ZIPPED_FRAME : 0;

    if(zip)
        memcpy(message+1, frame, 1024);
    else
        eds_zip_function(frame, message+1, NULL);

    eds_hal_send(message, 1025);

    return 0;
}

bool eds_query_animation_status() {
    uint16_t message = (PROTOCOL_QUERY << 16) + QUERY_IS_ANIMATION_RUNNING;
    eds_hal_send(&message, 2);

    eds_hal_recv(&is_animation_running, 1);

    return is_animation_running;
}

int eds_start_animation() {

    if(!is_animation_running) {
        eds_hal_send(PROTOCOL_TOGGLE_ANIMATION, 1);
        is_animation_running = true;
    }
    return 0;
}
int eds_stop_animation() {

    if(is_animation_running) {
        eds_hal_send(PROTOCOL_TOGGLE_ANIMATION, 1);
        is_animation_running = false;
    }
    return 0;
}

enum eds_fsm_states {
    FSM_WAIT_MESSAGE,
    FSM_NEW_MESSAGE,
    FSM_QUERY,
    FSM_CONTROL,
    FSM_RECV_FRAME,
    FSM_MAX_STATES
};
static int eds_fsm_state = FSM_WAIT_MESSAGE;
static uint8_t current_frame[1024];

/*
 *  @return 0 on no error
 */
int eds_decode_message(uint8_t *payload, int n) {
    int i = 0;  //consumed bytes
    static int received_frame_bytes = 0;

    while(i < n) {
        switch(eds_fsm_state) {
        case FSM_WAIT_MESSAGE:
            eds_fsm_state = FSM_NEW_MESSAGE;
            break;

        case FSM_NEW_MESSAGE:
            if(payload[i] && PROTOCOL_QUERY) {
                eds_fsm_state = FSM_QUERY;
                i++;
            } else if (payload[i] >= PROTOCOL_SET_FREQ) {
                eds_fsm_state = FSM_CONTROL;
            } else {
                eds_fsm_state = FSM_RECV_FRAME;
                received_frame_bytes = 0;
                i++;
            }
            eds_hal_send_byte(RESPONSE_ACK);
            break;

        case FSM_QUERY:
            if(payload[i] == QUERY_IS_ANIMATION_RUNNING)
                eds_hal_send_byte(is_animation_running);
        
            if(payload[i] == QUERY_BUFFER_SIZE)
                eds_hal_send_byte(10);

            if(payload[i] == QUERY_SUPPORTED_FX)
                eds_hal_send_byte(0x00);    //  still dummy
        
            i++;
            eds_fsm_state = FSM_WAIT_MESSAGE;
            break;
        
        case FSM_RECV_FRAME:
            current_frame[received_frame_bytes++] = payload[i++];
            if(received_frame_bytes == 1024) {
                eds_hal_display_show(current_frame);
                eds_fsm_state = FSM_WAIT_MESSAGE;
            }
            break;

        default:
            eds_fsm_state = FSM_WAIT_MESSAGE;
        }
        
    }

    return 0;
}