/* Test-only renderer witness. No pixels or successful scene operation are
 * simulated; record exact dispatch arguments and collision state at dispatch. */
#include <stdint.h>
void fixture_scene_enabled(void *render,uint32_t enabled) {
    uint32_t *log=(uint32_t *)0x1805000,*control=(uint32_t *)0x1805100;
    ++log[0];log[1]=(uintptr_t)render;log[2]=enabled;
    log[3]=control[0]?*(uint32_t *)(uintptr_t)control[0]:0x13579bdf;
    if(control[1])*(uint32_t *)(uintptr_t)control[1]=control[2];
}
