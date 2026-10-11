/* Test boundary for formatted movement tracking, including callback mutation. */
#include <stdarg.h>
#include <stdint.h>
void fixture_floor_transition_print(uint32_t *context, const char *format, ...) {
    uint32_t *record = context+4+context[0]++*16;
    va_list args; va_start(args, format);
    record[0] = (uintptr_t)format; record[1] = va_arg(args, uint32_t);
    for (unsigned i=0; i<6; ++i) {
        union { double number; uint64_t bits; } value = { .number=va_arg(args, double) };
        record[2+i*2] = value.bits; record[3+i*2] = value.bits>>32;
    }
    va_end(args);
    record[14] = *(uint32_t *)(uintptr_t)(0x1808000+0x1528);
    record[15] = *(uint32_t *)(uintptr_t)(0x1808000+12);
    if (context[1]==1) *(uint32_t *)(uintptr_t)context[2] = context[3];
    if (context[1]==2) *(uint8_t *)(uintptr_t)context[2] = context[3];
}
