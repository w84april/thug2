/* Test-only formatted-output boundary. Preserve raw integer/double argument
 * words and format pointers without invoking a host formatter or OS logger. */
#include <stdarg.h>
#include <stdint.h>
void fixture_compression_print(uint32_t *context, const char *format, ...) {
    uint32_t *record = context + 4 + context[0]++ * 4;
    va_list args;
    va_start(args, format);
    record[0] = (uintptr_t)format;
    if (format[8] == '/') {
        union { double value; uint64_t bits; } value = { .value = va_arg(args, double) };
        record[1] = 2; record[2] = value.bits; record[3] = value.bits >> 32;
    } else {
        record[1] = 1; record[2] = va_arg(args, uint32_t); record[3] = 0;
    }
    va_end(args);
}
