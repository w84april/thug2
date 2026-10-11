#ifndef THUG_SCRIPT_CACHE_H
#define THUG_SCRIPT_CACHE_H
#include "symbols.h"
#include "../core/lookup.h"
#include "../core/lzss.h"
typedef struct ThugScriptCacheEntry {
    uint32_t name;
    uint8_t *program;
    uint32_t references;
    struct ThugScriptCacheEntry *next, *previous;
} ThugScriptCacheEntry;
typedef struct {
    uint8_t unknown[0x14];
    ThugObjectLookupTable *table;
    ThugScriptCacheEntry *first, *last;
    uint8_t discard_immediately, padding[3];
} ThugScriptCache;
/* Original 6f3558, 6f3560, 6f3568/6c, and 68ff68. Cache construction and
 * destruction are not yet recovered; callers supply initialized instances.
 * The heap pointer lifts the original memory-manager field at manager+124. */
extern ThugScriptCache *thug_script_cache;
extern uint32_t thug_script_cache_pool_index;
extern ThugFixedPool *thug_script_cache_pools[2];
extern ThugHeapState *thug_script_cache_heap;
extern ThugLzssState thug_script_decoder;
void thug_script_cache_prepend(ThugScriptCache *, ThugScriptCacheEntry *);
void thug_script_cache_unlink(ThugScriptCache *, ThugScriptCacheEntry *);
void *thug_script_cache_allocate(uint32_t size, const ThugMemory *);
void thug_script_cache_free(void *, const ThugMemory *);
void thug_script_cache_evict(ThugScriptCache *, ThugScriptCacheEntry *, const ThugMemory *);
/* Requires an active pool and enough idle entries to satisfy the heap request. */
void thug_script_cache_trim(ThugScriptCache *, uint32_t bytes, uint32_t unused_name, const ThugMemory *);
void thug_script_cache_release(ThugScriptCache *, uint32_t name, const ThugMemory *);
uint8_t *thug_script_cache_acquire(ThugScriptCache *, uint32_t name, const ThugMemory *);
void thug_script_cache_reload(ThugScriptCache *, uint32_t name, const ThugMemory *);
/* Internal loader contract: valid bytecode and encoded scratch size <= 20000.
 * The optional global cache must be initialized if provided. */
ThugScriptSymbol *thug_script_register_script(const uint8_t *, uint32_t size,
    uint32_t name, uint32_t body_checksum, const char *filename, const ThugMemory *);
#endif
