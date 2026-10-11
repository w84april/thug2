#include "memory.h"
/* 0x004015d0. Array storage is not initialized by this allocation wrapper. */
void *thug_allocate_array_storage(uint32_t size, const ThugMemory *memory) {
    return memory->allocate(memory->context,size,1);
}
/* 0x00401cc0. Ordinary allocation followed by an exact-size zero fill. */
void *thug_allocate_zeroed(uint32_t size, const ThugMemory *memory) {
    uint8_t *result = memory->allocate(memory->context, size, 1);
    if (result) for (uint32_t i = 0; i < size; ++i) result[i] = 0;
    return result;
}
