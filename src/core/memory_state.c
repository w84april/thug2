#include "memory_state.h"

/* 0x005ba3b0. Membership is an unsigned range test, without alignment checks. */
uint32_t thug_pool_contains(const ThugFixedPool *pool, const void *allocation) {
    uint32_t address = (uintptr_t)allocation;
    return pool->start <= address && address < pool->end;
}
/* 0x005ba3d0. Empty allocation changes nothing; count/peak compare as signed. */
void *thug_pool_allocate(ThugFixedPool *pool) {
    uint32_t *allocation = pool->free;
    if (allocation) {
        ++pool->in_use;
        if ((int32_t)pool->peak < (int32_t)pool->in_use) pool->peak = pool->in_use;
        pool->free = (uint32_t *)(uintptr_t)*allocation;
    }
    return allocation;
}
/* 0x005ba400. The block's first word becomes a link; other bytes survive. */
void thug_pool_release(ThugFixedPool *pool, void *allocation) {
    --pool->in_use;
    *(uint32_t *)allocation = (uintptr_t)pool->free;
    pool->free = allocation;
}
/* 0x005bc530. Address subtraction wraps as a 32-bit word. */
uint32_t thug_heap_gap(const ThugHeapGap *gap) {
    uint32_t low = gap->lower ? gap->lower->boundary : gap->low;
    return (gap->upper ? gap->upper->boundary : gap->high) - low;
}
/* 0x005ba4f0. Largest free-list block or the arena gap, whichever is larger. */
uint32_t thug_heap_largest_free(const ThugHeapState *heap) {
    uint32_t largest = 0;
    for (const ThugHeapFreeBlock *block = heap->free_blocks->first; block; block = block->next)
        if (largest <= block->size) largest = block->size;
    uint32_t gap = thug_heap_gap(heap->gap);
    return gap <= largest ? largest : gap;
}
