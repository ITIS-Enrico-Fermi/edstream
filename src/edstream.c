#include "edstream.h"
#include "edstream_hal.h"

#define LOG_LOCAL_LEVEL ESP_LOG_NONE
#include "esp_log.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include <string.h>

static bool is_animation_running = false;
static int refresh_rate = 20;  // ms
static eds_zip_function_t eds_zip_function = eds_zip_deflate;

static uint8_t framebuffer[FRAME_SIZE * MAX_FRAME_NUMBER];
static int framebuffer_size = 0;

/*
 *  @brief Sends a frame to display device (that controls the display)
 * 
 *  @param frame    1024 byte array representing a 128x64 frame
 *  @param save     True if device should save the frame
 *  @param zip      True if the frame should be zipped before sending
 * 
 *  You can provide a Deflate function with eds_zip_function_set()
 */
int eds_send_frame(const uint8_t *frame, bool save, bool zip)
{
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

bool eds_query_animation_status()
{
    uint16_t message = (PROTOCOL_QUERY << 16) + QUERY_IS_ANIMATION_RUNNING;
    eds_hal_send(&message, 2);

    eds_hal_recv(&is_animation_running, 1);

    return is_animation_running;
}

void eds_show_animation_task(void* pvParameters)
{
    int local_frame_counter = 0;
    ESP_LOGD("SHOW", "Entering while loop");
    while (is_animation_running) {
        eds_hal_display_show(framebuffer + local_frame_counter*FRAME_SIZE);
        local_frame_counter++;
        local_frame_counter %= framebuffer_size;
        vTaskDelay(refresh_rate/portTICK_PERIOD_MS);
    }
    ESP_LOGD("SHOW", "Exiting while loop of show_animation_task");
    vTaskDelete(NULL);
}

int eds_start_animation()
{
    if(!is_animation_running) {
        ESP_LOGD("START", "Start automation");
        // eds_hal_send(PROTOCOL_TOGGLE_ANIMATION, 1);
        is_animation_running = true;
        xTaskCreate(eds_show_animation_task, "show_animation_task", 8192, NULL, 5, NULL);  // TODO: Guru meditation error
    }
    return 0;
}
int eds_stop_animation()
{
    if(is_animation_running) {
        // eds_hal_send(PROTOCOL_TOGGLE_ANIMATION, 1);
        is_animation_running = false;  // show_animation_task exits from loop and destroys himself
    }
    return 0;
}

int eds_send_ack(void)
{
    ESP_LOGD("ACK", "Sending ACK to controller");
    return eds_hal_send_byte(RESPONSE_ACK);
}

void eds_toggle_animation(void)
{
    ESP_LOGD("TOGGLE", "toggle animation");
    if (is_animation_running)
        eds_stop_animation();
    else
        eds_start_animation();
}

void eds_clear_framebuffer(void)
{
    framebuffer_size = 0;
}


enum eds_fsm_states {
    FSM_WAIT_MESSAGE,
    FSM_NEW_MESSAGE,
    FSM_QUERY,
    FSM_CONTROL,
    FSM_RECV_FRAME,
    FSM_CLEAR_BUF,
    FSM_TOGGLE_ANIMATION,
    FSM_SAVE_FRAME,
    FSM_MAX_STATES
};

static int eds_fsm_state = FSM_WAIT_MESSAGE;

/*
 *  @return 0 on no error
 */
int eds_decode_message(const uint8_t *payload, int n)
{
    int i = 0;  //consumed bytes
    static int received_frame_bytes = 0;
    static int frame_counter = 0;
    bool is_zipped = false;

    ESP_LOGI("FSM", "Called FSM with %d bytes of payload", n);

    while(i < n) {
        switch(eds_fsm_state) {
        case FSM_WAIT_MESSAGE:
            eds_fsm_state = FSM_NEW_MESSAGE;
            break;

        case FSM_NEW_MESSAGE:
            if (payload[i] & PROTOCOL_QUERY) {
                eds_fsm_state = FSM_QUERY;
            } else if (payload[i] & PROTOCOL_CLEAR_BUF) {
                eds_fsm_state = FSM_CLEAR_BUF;
            } else if (payload[i] & PROTOCOL_TOGGLE_ANIMATION) {
                eds_fsm_state = FSM_TOGGLE_ANIMATION;
            } else if (payload[i] & PROTOCOL_SET_FREQ) {
                eds_fsm_state = FSM_CONTROL;
            } else if (payload[i] & PROTOCOL_SAVE_FRAME) {
                eds_fsm_state = FSM_SAVE_FRAME;
            } else {
                eds_fsm_state = FSM_WAIT_MESSAGE;
            }
            ESP_LOGD("FSM", "Payload is i-1]: %x [i]: %x and next state will be %d\n", payload[i-1], payload[i], eds_fsm_state);
            eds_send_ack();
            break;

        case FSM_QUERY:
            if(payload[i] == QUERY_IS_ANIMATION_RUNNING)
                eds_hal_send_byte(is_animation_running);
        
            if(payload[i] == QUERY_BUFFER_SIZE)
                eds_hal_send_byte(10);

            if(payload[i] == QUERY_SUPPORTED_FX)
                eds_hal_send_byte(0x00);
        
            i++;
            eds_fsm_state = FSM_WAIT_MESSAGE;
            break;
        
        case FSM_RECV_FRAME:
            framebuffer[(received_frame_bytes++) + (FRAME_SIZE*frame_counter)] = payload[i++];
            ESP_LOGD("FSM", "Bytes counter: %d", received_frame_bytes);
            if(received_frame_bytes == 1024) {
                ESP_LOGI("FSM", "Saved...");
                eds_fsm_state = FSM_WAIT_MESSAGE;
                framebuffer_size++;
                frame_counter++;
                eds_send_ack();
            }
            break;

        case FSM_CLEAR_BUF:
            ESP_LOGD("FSM", "Clear buffer");
            frame_counter = 0;
            eds_clear_framebuffer();
            eds_fsm_state = FSM_WAIT_MESSAGE;
            i++;
            break;

        case FSM_TOGGLE_ANIMATION:
            ESP_LOGD("FSM", "Toggle animation");
            eds_toggle_animation();
            eds_fsm_state = FSM_WAIT_MESSAGE;
            i++;
            break;
        
        case FSM_SAVE_FRAME:
            ESP_LOGD("FSM", "Save frame");
            is_zipped = payload[i] & PROTOCOL_ZIPPED_FRAME;
            i++;
            received_frame_bytes = 0;
            eds_fsm_state = FSM_RECV_FRAME;
            ESP_LOGD("FSM", "Exiting from save frame state");
            break;

        default:
            eds_fsm_state = FSM_WAIT_MESSAGE;
        }
        
    }

    return 0;
}