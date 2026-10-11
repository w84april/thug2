#include "random.h"
ThugRandomState thug_random_state, thug_random_alternate_state;
uint32_t thug_crt_random_state=1;
/* 00623ba3. The CRT recurrence differs from both engine generators below. */
uint32_t thug_crt_random(void) {
    thug_crt_random_state=thug_crt_random_state*UINT32_C(0x343fd)+UINT32_C(0x269ec3);
    return (thug_crt_random_state>>16)&0x7fff;
}
static int32_t next(ThugRandomState *state, uint32_t limit) {
    uint32_t value = state->multiplier * state->value + state->increment;
    state->value = value;
    state->multiplier = (state->multiplier ^ value) + (uint32_t)((int32_t)value >> 4);
    state->increment += (uint32_t)((int32_t)value >> 3) - UINT32_C(0x10101010);
    return (int32_t)((value & 0xffff) * limit) >> 16;
}
/* 0x00403de0, 0x00403e30. Preserve 32-bit wrap and the final arithmetic shift,
 * including negative results for out-of-range limits. */
int32_t thug_random_range(uint32_t limit) { return next(&thug_random_state, limit); }
int32_t thug_random_alternate_range(uint32_t limit) { return next(&thug_random_alternate_state, limit); }
