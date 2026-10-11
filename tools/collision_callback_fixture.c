/* Test instrumentation only, not recovered game code. This separate module
 * shares the production module's memory and records/mutates callback results.
 * Its stack is linked away from the engine stack. The x86 oracle uses a hook
 * with the same operations; neither substitutes for a real game callback. */
#include <stdint.h>

void record_hit(uint8_t *result) {
    volatile uint32_t *control = (volatile uint32_t *)0x02000400;
    uint8_t *log = (uint8_t *)(0x02100000 + control[1] * 80);
    for (unsigned i = 0; i < 80; ++i) log[i] = result[i];
    ++control[1];
    if (control[0] & 1) {
        for (unsigned i = 0; i < 80; ++i)
            if (i < 0x3c || i >= 0x40) result[i] ^= 0x5a;
    }
    if (control[0] & 2) *(uint8_t *)(uintptr_t)control[2] ^= 1;
}
