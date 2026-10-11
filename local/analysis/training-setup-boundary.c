/* Test-only breakpoint; no scene-object destruction or successful return. */
#include <stdint.h>
uint8_t fixture_missing_kill(void *params,void *script){
    volatile uint32_t *p=(void *)(uintptr_t)0x100e000;
    p[0]=0x5a5030;p[1]=(uintptr_t)params;p[2]=(uintptr_t)script;++p[3];__builtin_trap();
}
