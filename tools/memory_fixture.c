/* Test-only deterministic allocator. Not the game's memory manager. */
#include <stdint.h>

static void event(uint32_t *context, uint32_t kind, uint32_t a, uint32_t b, uint32_t c) {
    uint32_t *log = (uint32_t *)0x02001000 + context[2]++ * 4;
    log[0] = kind; log[1] = a; log[2] = b; log[3] = c;
}

void *fixture_allocate(uint32_t *context, uint32_t size, uint32_t route) {
    uint32_t pointer = (context[0] + 31u) & ~15u;
    if (pointer > context[1] || size + 16u > context[1] - pointer) __builtin_trap();
    context[0] = pointer + size + 16u;
    uint8_t *bytes = (uint8_t *)(uintptr_t)pointer;
    for (uint32_t i = 0; i < size; ++i) bytes[i] = 0xa5;
    event(context, 1, size, route, pointer);
    return bytes;
}

void fixture_release(uint32_t *context, void *pointer) {
    event(context, 2, (uintptr_t)pointer, 0, 0);
}

void fixture_temp_scope(uint32_t *context, uint32_t enter) {
    context[3] = enter;
    event(context, 3, enter, 0, 0);
}
