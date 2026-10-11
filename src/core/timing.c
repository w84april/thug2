#include "timing.h"
#include "number.h"
#include "../platform/math.h"
uint32_t thug_frame_counter, thug_timer_origin, thug_timer_offset;
float thug_frame_rate = 60, thug_time_scale = 1;
float thug_frame_length_scale = 1;

/* 0x005beaa0. Retain the wider x87 result until the caller's float store. */
double thug_frame_duration(void) {
    return thug_platform_round_x87_single((double)thug_frame_length_scale * (double)0.01666666753590107f);
}

static double load_unsigned(uint32_t value) {
    /* FILD loads signed exactly; only the high-half case adds 2^32, rounding
     * at PC24 before the following multiply. This is not a direct float cast. */
    double number = (int32_t)value;
    return (int32_t)value < 0 ? thug_platform_round_x87_single(number + 0x1p32) : number;
}
/* 0x005be970. Frame rate must be a positive finite gameplay rate. */
uint32_t thug_frame_time(void) {
    float factor = (float)thug_platform_round_x87_single(1000.0 / thug_frame_rate);
    return thug_truncate_double_low_word(thug_platform_multiply_x87_single(load_unsigned(thug_frame_counter), factor));
}
/* 0x0044ece0. Subtraction wraps before conversion; level offset is added by
 * callers such as 0x00504b40, not by this timer routine. */
uint32_t thug_elapsed_time(void) {
    uint32_t delta = thug_frame_time() - thug_timer_origin;
    return thug_truncate_double_low_word(thug_platform_multiply_x87_single(load_unsigned(delta), thug_time_scale));
}
/* 0x00420250. Offset and subtraction use wrapping unsigned arithmetic. */
uint32_t thug_time_since(uint32_t timestamp) {
    return thug_elapsed_time()+thug_timer_offset-timestamp;
}
