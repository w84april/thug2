#ifndef THUG_CORE_NUMBER_H
#define THUG_CORE_NUMBER_H
#include <stdint.h>
double thug_sign_nonnegative(float value);
double thug_acos_approximate(float value);
double thug_max_number(float left, float right);
double thug_clamp_number(float value,float minimum,float maximum);
double thug_min_three(float first,float second,float third);

/* Low 32 bits of MSVC's _ftol2 (0x006236fc), for the f32/PC24 caller paths recovered
 * here. Invalid conversion gives integer-indefinite, whose low word is zero.
 * This does not emulate arbitrary extended-precision inputs to the CRT helper. */
static inline uint32_t thug_truncate_double_low_word(double value) {
    if (!(value >= -0x1p63 && value < 0x1p63)) return 0;
    return (uint32_t)(int64_t)value;
}
static inline uint32_t thug_truncate_low_word(float value) { return thug_truncate_double_low_word(value); }
#endif
