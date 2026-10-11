/* Test-only breakpoint. No skeleton-loading behavior is supplied. */
#include <stdint.h>
uint8_t fixture_missing_load_skeleton(void *params,void *script) {
    volatile uint32_t *boundary=(volatile uint32_t *)(uintptr_t)0x100e000;
    boundary[0]=0x445640;boundary[1]=(uintptr_t)params;boundary[2]=(uintptr_t)script;
    ++boundary[3];
    __builtin_trap();
}
