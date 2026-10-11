/* Test-only formatted-output boundary; record original raw argument words. */
#include <stdarg.h>
#include <stdint.h>
void fixture_network_print(uint32_t *context, const char *format, ...) {
    uint32_t *record = context + 4 + context[0]++ * 4;
    uint32_t count = format[4] == 'C' ? 0 : 2;
    record[0] = (uintptr_t)format; record[1] = count;
    va_list args; va_start(args, format);
    record[2] = count ? va_arg(args, uint32_t) : 0;
    record[3] = count ? va_arg(args, uint32_t) : 0;
    va_end(args);
}
