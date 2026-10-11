/* Test-only observation of the optional no-argument initialization callback. */
#include <stdint.h>
void fixture_factory_registration_callback(void) {
    volatile uint32_t *log = (volatile uint32_t *)0x1803000;
    volatile uint32_t *manager = (volatile uint32_t *)(uintptr_t)log[1];
    uint32_t index = log[0]++;
    log[8 + index * 4] = manager[0x44 / 4];
    log[9 + index * 4] = manager[0x40 / 4];
    log[10 + index * 4] = manager[0x48 / 4];
    log[11 + index * 4] = manager[0x4c / 4];
    if (log[2]) manager[0x44 / 4] = log[3];
}
