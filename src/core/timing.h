#ifndef THUG_CORE_TIMING_H
#define THUG_CORE_TIMING_H
#include <stdint.h>
/* Lifted globals 7d1ec8, 684fd0, 696d64, 67d7c0, 696d60. The producer of the
 * frame counter is not recovered here. The original ignores its upper word. */
extern uint32_t thug_frame_counter, thug_timer_origin, thug_timer_offset;
extern float thug_frame_rate, thug_time_scale;
/* 684fc8 scales the fixed 1/60 second tick; its producer is not recovered. */
extern float thug_frame_length_scale;
uint32_t thug_frame_time(void);
uint32_t thug_elapsed_time(void);
uint32_t thug_time_since(uint32_t timestamp);
double thug_frame_duration(void);
#endif
