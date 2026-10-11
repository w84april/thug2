/* Test boundary: insert an initialized instance while deferred code is running,
 * exposing whether each recovered list walk captures next before or after it. */
#include "script_execute_callbacks.c"
uint32_t fixture_lifetime_native(uint32_t *parameters, uint32_t *script) {
    uint32_t result = fixture_execute_native(parameters, script);
    if (CONTEXT[2] == 6) {
        uint32_t *added = (uint32_t *)(uintptr_t)CONTEXT[3];
        uint32_t *next = (uint32_t *)(uintptr_t)script[0];
        added[0] = (uintptr_t)next; added[1] = (uintptr_t)script;
        if (next) next[1] = (uintptr_t)added;
        script[0] = (uintptr_t)added;
    }
    return result;
}
