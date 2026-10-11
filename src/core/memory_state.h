#ifndef THUG_MEMORY_STATE_H
#define THUG_MEMORY_STATE_H
#include <stdint.h>
typedef struct {
    uint32_t start, end, unknown_8, unknown_c, in_use;
    uint32_t *free;
    uint8_t unknown_18_to_57[0x40];
    uint32_t peak;
} ThugFixedPool;
typedef struct ThugHeapFreeBlock { struct ThugHeapFreeBlock *next; uint32_t size; } ThugHeapFreeBlock;
typedef struct { uint8_t unknown[0x14]; ThugHeapFreeBlock *first; } ThugHeapFreeList;
typedef struct { uint8_t unknown[0x2c]; uint32_t boundary; } ThugHeapBoundary;
typedef struct {
    uint32_t unknown_0, low, unknown_8, high;
    ThugHeapBoundary *lower, *upper;
} ThugHeapGap;
typedef struct {
    uint8_t unknown[0x24]; ThugHeapGap *gap;
    uint32_t unknown_28, unknown_2c; ThugHeapFreeList *free_blocks;
} ThugHeapState;

uint32_t thug_pool_contains(const ThugFixedPool *, const void *);
void *thug_pool_allocate(ThugFixedPool *);
void thug_pool_release(ThugFixedPool *, void *);
uint32_t thug_heap_gap(const ThugHeapGap *);
uint32_t thug_heap_largest_free(const ThugHeapState *);
#endif
