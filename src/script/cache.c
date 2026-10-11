#include "cache.h"
#include "tokens.h"
#include "../core/compress.h"
#include "../core/checksum.h"
#include <stddef.h>

ThugScriptCache *thug_script_cache;
uint32_t thug_script_cache_pool_index;
ThugFixedPool *thug_script_cache_pools[2];
ThugHeapState *thug_script_cache_heap;
ThugLzssState thug_script_decoder;
_Static_assert(sizeof(ThugScriptCacheEntry) == 20, "Original cache entry");
_Static_assert(sizeof(ThugScriptCache) == 36, "Original cache");

/* 0x00475a40. Idle entries prepend; the tail is the oldest idle entry. */
void thug_script_cache_prepend(ThugScriptCache *cache, ThugScriptCacheEntry *entry) {
    entry->previous = NULL; entry->next = cache->first; cache->first = entry;
    if (entry->next) entry->next->previous = entry;
    if (!cache->last) cache->last = cache->first;
}
/* 0x00475a70. Also used for active entries whose links are already null. */
void thug_script_cache_unlink(ThugScriptCache *cache, ThugScriptCacheEntry *entry) {
    if (entry->previous) entry->previous->next = entry->next;
    if (entry->next) entry->next->previous = entry->previous;
    if (cache->first == entry) cache->first = entry->next;
    if (cache->last == entry) cache->last = entry->previous;
    entry->next = NULL; entry->previous = NULL;
}
/* 0x00475ac0. The selected fixed pool ignores the requested size. */
void *thug_script_cache_allocate(uint32_t size, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_cache_pools[thug_script_cache_pool_index];
    return pool ? thug_pool_allocate(pool) : memory->allocate(memory->context, size, 1);
}
/* 0x00475b00. Try current pool, then the other pool, then the generic heap. */
void thug_script_cache_free(void *entry, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_cache_pools[thug_script_cache_pool_index];
    if (pool && thug_pool_contains(pool, entry)) { thug_pool_release(pool, entry); return; }
    pool = thug_script_cache_pools[thug_script_cache_pool_index ^ 1];
    if (pool && thug_pool_contains(pool, entry)) { thug_pool_release(pool, entry); return; }
    memory->release(memory->context, entry);
}
/* 0x00475b60. Remove from the hash table before unlinking and freeing storage. */
void thug_script_cache_evict(ThugScriptCache *cache, ThugScriptCacheEntry *entry, const ThugMemory *memory) {
    thug_object_table_remove(cache->table, &entry->name, memory);
    thug_script_cache_unlink(cache, entry);
    if (entry->program) memory->release(memory->context, entry->program);
    thug_script_cache_free(entry, memory);
}
/* 0x00475bd0. Preserve the signed comparisons, 128-byte reserve and second
 * phase's 100-entry threshold. The original first phase has no empty-list guard. */
void thug_script_cache_trim(ThugScriptCache *cache, uint32_t bytes, uint32_t unused_name, const ThugMemory *memory) {
    (void)unused_name;
    while ((int32_t)(thug_heap_largest_free(thug_script_cache_heap) - 128) < (int32_t)bytes)
        thug_script_cache_evict(cache, cache->last, memory);
    while ((int32_t)thug_script_cache_pools[thug_script_cache_pool_index]->in_use >= 100 && cache->last)
        thug_script_cache_evict(cache, cache->last, memory);
}
/* 0x00475d60. This lookup uses the supplied name without resolving aliases. */
void thug_script_cache_release(ThugScriptCache *cache, uint32_t name, const ThugMemory *memory) {
    ThugScriptCacheEntry *entry = thug_object_table_find(cache->table, &name, 1);
    if (entry && !--entry->references) {
        if (cache->discard_immediately) thug_script_cache_evict(cache, entry, memory);
        else thug_script_cache_prepend(cache, entry);
    }
}
/* 0x00475e80. Resolve aliases before lookup; a non-script symbol rejects even
 * a cached name. On a miss, copy/decompress and prepare the complete bytecode. */
uint8_t *thug_script_cache_acquire(ThugScriptCache *cache, uint32_t name, const ThugMemory *memory) {
    const ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (symbol) { if (symbol->type != 7) return NULL; name = symbol->name; }
    ThugScriptCacheEntry *entry = thug_object_table_find(cache->table, &name, 1);
    if (entry) { ++entry->references; thug_script_cache_unlink(cache, entry); return entry->program; }
    if (!symbol) return NULL;
    const uint32_t *stored = (const uint32_t *)(uintptr_t)symbol->value;
    uint32_t size = stored[1], compressed_size = stored[2];
    thug_script_cache_trim(cache, size, name, memory);
    entry = thug_script_cache_allocate(20, memory);
    if (entry) { entry->name = 0; entry->program = NULL; entry->references = 0; entry->next = NULL; entry->previous = NULL; }
    memory->temp_scope(memory->context, 1);
    uint8_t *program = memory->allocate(memory->context, size, 0);
    memory->temp_scope(memory->context, 0);
    stored = (const uint32_t *)(uintptr_t)symbol->value;
    if (compressed_size < size) thug_lzss_decode_unchecked(&thug_script_decoder, (const uint8_t *)(stored + 3), program, compressed_size);
    else for (uint32_t i = 0; i < size; ++i) program[i] = ((const uint8_t *)(stored + 3))[i];
    thug_script_prepare_bytecode(program);
    entry->program = program; entry->references = 1; entry->name = name;
    thug_object_table_insert(cache->table, &name, entry, memory);
    return entry->program;
}
/* 0x00475fd0. Requires a replacement script for an existing entry. The saved
 * count is restored verbatim: zero is not reinserted into the idle list. */
void thug_script_cache_reload(ThugScriptCache *cache, uint32_t name, const ThugMemory *memory) {
    ThugScriptCacheEntry *entry = thug_object_table_find(cache->table, &name, 1);
    if (!entry) return;
    uint32_t references = entry->references;
    thug_script_cache_evict(cache, entry, memory);
    thug_script_cache_acquire(cache, name, memory);
    entry = thug_object_table_find(cache->table, &name, 1);
    entry->references = references;
}
/* 0x0046fe40. Original input=EBX, size=EAX, then name/checksum/filename on
 * the stack. Compression is retained only when it is smaller than the input. */
ThugScriptSymbol *thug_script_register_script(const uint8_t *input, uint32_t size,
    uint32_t name, uint32_t checksum, const char *filename, const ThugMemory *memory) {
    ThugScriptSymbol *symbol = thug_script_symbol_create(name, memory);
    symbol->type = 7;
    uint8_t *scratch = memory->allocate(memory->context, 20000, 0);
    uint32_t encoded = thug_lzss_encode_unchecked(input, scratch, size, 0, NULL, memory);
    if ((int32_t)encoded >= (int32_t)size) {
        for (uint32_t i = 0; i < size; ++i) scratch[i] = input[i];
        encoded = size;
    }
    uint32_t *stored = memory->allocate(memory->context, encoded + 12, 0);
    stored[0] = checksum; stored[1] = size; stored[2] = encoded;
    if ((int32_t)encoded > 0) for (uint32_t i = 0; i < encoded; ++i) ((uint8_t *)(stored + 3))[i] = scratch[i];
    symbol->value = (uintptr_t)stored;
    memory->release(memory->context, scratch);
    if (thug_script_cache) thug_script_cache_reload(thug_script_cache, name, memory);
    symbol->unknown_8 = thug_crc32_string(filename);
    return symbol;
}
