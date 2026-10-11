#include "text.h"
#include "math.h"
#include <stddef.h>
const ThugTextPlatform *thug_text_platform;
ThugTextLocale *thug_text_locale;
int32_t thug_text_mb_max = 1;
void thug_text_signed_decimal(char *out, int32_t value) {
    uint32_t magnitude = (uint32_t)value;
    if (value < 0) { *out++ = '-'; magnitude = 0u-magnitude; }
    char digits[10]; uint32_t count = 0;
    do { digits[count++] = (char)('0'+magnitude%10); magnitude /= 10; } while (magnitude);
    while (count) *out++ = digits[--count];
    *out = 0;
}
/* The old CRT first produces seventeen significant decimal digits, then
 * rounds to one fractional digit, with halves away from zero. Its nonfinite
 * mantissa text is rounded as character data too, producing "1.$" here.
 * Work from the f32 bits: large integers need up to 128 bits, but this fixed
 * precision never needs the entire fractional decimal expansion. */
void thug_text_fixed_one(char *out, float value) {
    uint32_t bits; __builtin_memcpy(&bits,&value,4);
    uint32_t magnitude = bits & 0x7fffffff, exponent = magnitude >> 23;
    if ((bits >> 31) && magnitude) *out++ = '-';
    if (exponent == 255) { *out++ = '1'; *out++ = '.'; *out++ = '$'; *out = 0; return; }
    uint32_t mantissa = (magnitude & 0x7fffff) | (exponent ? 0x800000 : 0);
    int32_t power = (exponent ? (int32_t)exponent-127 : -126)-23;
    if (power <= 0) {
        uint32_t scaled = mantissa*10, shift = (uint32_t)-power, rounded;
        if (!shift) rounded = scaled;
        else if (shift >= 32) rounded = 0;
        else rounded = (scaled + (1u << (shift-1))) >> shift;
        thug_text_signed_decimal(out,(int32_t)(rounded/10));
        while (*out) ++out;
        *out++ = '.'; *out++ = (char)('0'+rounded%10); *out = 0; return;
    }
    uint32_t words[4] = {0,0,0,0}, limb = (uint32_t)power/32, shift = (uint32_t)power%32;
    words[limb] = mantissa << shift;
    if (shift && limb < 3) words[limb+1] = mantissa >> (32-shift);
    char reversed[40], digits[40]; uint32_t count = 0, nonzero;
    do {
        uint64_t remainder = 0; nonzero = 0;
        for (int i = 3; i >= 0; --i) {
            uint64_t word = (remainder << 32) | words[i];
            words[i] = (uint32_t)(word/10); remainder = word%10; nonzero |= words[i];
        }
        reversed[count++] = (char)('0'+remainder);
    } while (nonzero);
    for (uint32_t i = 0; i < count; ++i) digits[i] = reversed[count-1-i];
    if (count > 17) {
        if (digits[17] >= '5') {
            int i = 16;
            while (i >= 0 && digits[i] == '9') digits[i--] = '0';
            if (i >= 0) ++digits[i];
            else { digits[0] = '1'; for (uint32_t j = 1; j <= count; ++j) digits[j] = '0'; ++count; }
        }
        for (uint32_t i = 17; i < count; ++i) digits[i] = '0';
    }
    for (uint32_t i = 0; i < count; ++i) *out++ = digits[i];
    *out++ = '.'; *out++ = '0'; *out = 0;
}
/* 0x006254eb. Keep the CRT's locale branches, partial writes, truncation and
 * errno behavior. WideCharToMultiByte and GetLastError remain OS boundaries. */
uint32_t thug_text_convert_wide(const ThugTextLocale *locale, char *out,
    const uint16_t *in, uint32_t capacity) {
    uint32_t count = 0;
    int32_t substituted = 0, result;
    if (!out) {
        if (!locale->ctype_locale) { while (in[count]) ++count; return count; }
        result = thug_text_platform->wide_to_multibyte(locale->codepage,0,in,-1,NULL,0,NULL,&substituted);
        if (result && !substituted) return (uint32_t)result - 1;
    } else if (!capacity) return 0;
    else if (!locale->ctype_locale) {
        while (*in < 256) {
            out[count] = (char)*in;
            uint16_t value = *in++;
            if (!value) return count;
            if (++count >= capacity) return count;
        }
    } else if (thug_text_mb_max == 1) {
        const uint16_t *end = in;
        uint32_t left = capacity;
        while (left && *end) { ++end; --left; }
        if (left && !*end) capacity = (uint32_t)(end-in) + 1;
        result = thug_text_platform->wide_to_multibyte(locale->codepage,0,in,(int32_t)capacity,out,(int32_t)capacity,NULL,&substituted);
        if (result && !substituted) return (uint32_t)result - (out[result-1] == 0);
    } else {
        result = thug_text_platform->wide_to_multibyte(locale->codepage,0,in,-1,out,(int32_t)capacity,NULL,&substituted);
        if (result) { if (!substituted) return (uint32_t)result-1; }
        else if (!substituted && thug_text_platform->last_error() == 122) {
            while (count < capacity) {
                char bytes[8];
                result = thug_text_platform->wide_to_multibyte(locale->codepage,0,in,1,bytes,thug_text_mb_max,NULL,&substituted);
                if (!result || substituted) break;
                if (capacity < count + (uint32_t)result) return count;
                for (int32_t i = 0; i < result; ++i) {
                    out[count] = bytes[i];
                    if (!bytes[i]) return count;
                    ++count;
                }
                ++in;
            }
            if (count >= capacity) return count;
        }
    }
    thug_math_errno = 42;
    return UINT32_MAX;
}
/* 0x0062569c. The host owns current-thread locale selection. */
uint32_t thug_text_wcstombs(char *out, const uint16_t *in, uint32_t capacity) {
    return thug_text_convert_wide(thug_text_locale,out,in,capacity);
}
