#ifndef THUG_LOOKUP_H
#define THUG_LOOKUP_H
#include "memory.h"
#include "memory_state.h"
typedef struct ThugObjectLookupNode {
    uint32_t key;
    void *value;
    struct ThugObjectLookupNode *next;
} ThugObjectLookupNode;
typedef struct {
    uint32_t shift;
    ThugObjectLookupNode *buckets;
    uint32_t count, iteration_bucket;
    ThugObjectLookupNode *iteration_node;
    uint8_t flags, padding[3];
} ThugObjectLookupTable;
/* Original allocator slot 0 at 0x007d1808, used for 12-byte collision nodes. */
extern ThugFixedPool *thug_lookup_node_pool;
void *thug_object_table_find(const ThugObjectLookupTable *, const uint32_t *key, uint32_t unused);
ThugObjectLookupTable *thug_object_table_initialize(ThugObjectLookupTable *, uint32_t shift, const ThugMemory *);
uint32_t thug_object_table_insert(ThugObjectLookupTable *, const uint32_t *key, void *value, const ThugMemory *);
void thug_object_table_remove(ThugObjectLookupTable *, const uint32_t *key, const ThugMemory *);
uint8_t thug_object_table_next(ThugObjectLookupTable *);
typedef void (*ThugObjectVisitor)(void *value, void *context);
/* Overflow nodes precede the embedded head; next is captured before callbacks. */
void thug_object_table_visit(const ThugObjectLookupTable *, ThugObjectVisitor, void *);
#endif
