/* Test-only release schedule for cache trimming. Heap ownership/storage is a
 * platform boundary. Specified releases increase a modeled contiguous gap;
 * fixed-pool operations and the actual trim policy execute recovered code. */
#include "script_values_memory.c"
void fixture_cache_release(uint32_t *context, void *pointer) {
    fixture_values_release(context, pointer);
    uint32_t *entries = (uint32_t *)(uintptr_t)context[8];
    for (uint32_t i = 0; i < context[9]; ++i) {
        if (entries[i*2] == (uintptr_t)pointer) {
            *(uint32_t *)(uintptr_t)context[10] += entries[i*2+1];
            entries[i*2+1] = 0;
        }
    }
}
