#include "component_registration.h"
static uint32_t read32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value, p, 4);
    return value;
}
static void write32(uint8_t *p, uint32_t value) {
    __builtin_memcpy(p, &value, 4);
}
/* 0045f270. Factory identity is borrowed; only initialize is invoked here.
 * Preserve the three count reads and the increment before the no-argument call.
 * Offsets retain the original uint32 arithmetic, including aliasing storage. */
void thug_component_register_factory(void *manager, uint32_t type,
    uint32_t factory, ThugRegistrationInitialize initialize) {
    uint8_t *p = manager;
    write32(p + (uint32_t)(read32(p + 0x44) * 8u + 0x48u), type);
    write32(p + (uint32_t)(read32(p + 0x44) * 8u + 0x4cu), factory);
    write32(p + 0x44, read32(p + 0x44) + 1u);
    if (initialize) initialize();
}
