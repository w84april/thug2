#ifndef THUG_CORE_MEMORY_H
#define THUG_CORE_MEMORY_H
#include <stdint.h>

/* New platform adapter, not a reconstruction of the PC memory manager.
 * route 0 replaces 0x005bbae0(size); route 1 replaces the allocation at
 * 0x005bafc0(size, 1, 0). temp_scope brackets 0x005bb0e0/0x005bb110:
 * 0 exits, 1 enters the ordinary temporary heap (manager+0x124), and 2 enters
 * the compression heap (manager+0x110), 3 the debug heap (manager+0x154),
 * 4 the message heap (manager+0x12c), 5 the objective heap (manager+0x114),
 * and 6 the UI heap (manager+0x11c), 7 the named animation cache heap
 * (checksum 0x8f21a798, selected by 0x005baf50).
 * The port supplies their actual storage.
 * Internal loading routines, like the original, require successful allocation.
 */
typedef struct {
    void *context;
    void *(*allocate)(void *context, uint32_t size, uint32_t route);
    void (*release)(void *context, void *allocation);
    void (*temp_scope)(void *context, uint32_t enter);
    /* New host boundary for 0x005bb050: contiguous bytes available in the
     * selected heap. Required only by animation cache allocation paths. */
    uint32_t (*available)(void *context);
} ThugMemory;
void *thug_allocate_zeroed(uint32_t size, const ThugMemory *);
void *thug_allocate_array_storage(uint32_t size, const ThugMemory *);
#endif
