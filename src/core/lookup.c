#include "lookup.h"

/* 0x005b8060. Read each head value after visiting that bucket's overflow list. */
void thug_object_table_visit(const ThugObjectLookupTable *table, ThugObjectVisitor visit, void *context) {
    ThugObjectLookupNode *head = table->buckets;
    uint32_t count = UINT32_C(1) << (table->shift & 31);
    do {
        for (ThugObjectLookupNode *node = head->next, *next; node; node = next) {
            next = node->next;
            if (node->value) visit(node->value, context);
        }
        if (head->value) visit(head->value, context);
        ++head;
    } while (--count);
}
#include <stddef.h>

ThugFixedPool *thug_lookup_node_pool;
_Static_assert(sizeof(ThugObjectLookupTable) == 24, "Original lookup table");
/* 0x00588190. Shared, stateful table iterator. Start with bucket=-1 and node=0.
 * Empty inline buckets can still have collision nodes. The terminal bucket
 * value remains stored, so another call after exhaustion also returns false. */
uint8_t thug_object_table_next(ThugObjectLookupTable *table) {
    uint32_t count = 1u << (table->shift & 31);
    if (table->iteration_node) table->iteration_node = table->iteration_node->next;
    else if ((int32_t)table->iteration_bucket >= 0) return 0;
    if (!table->iteration_node) {
        do {
            ++table->iteration_bucket;
            if ((int32_t)table->iteration_bucket >= (int32_t)count) return 0;
            table->iteration_node = table->buckets + table->iteration_bucket;
        } while (!table->iteration_node->value && !table->iteration_node->next);
        if (!table->iteration_node->value) table->iteration_node = table->iteration_node->next;
    }
    return 1;
}
/* 0x0049fd90. The shift uses the low five bits; internal callers must select
 * a size that fits memory and provide successful allocation. */
ThugObjectLookupTable *thug_object_table_initialize(ThugObjectLookupTable *table, uint32_t shift, const ThugMemory *memory) {
    table->shift = shift;
    uint32_t count = 1u << (shift & 31);
    ThugObjectLookupNode *buckets = memory->allocate(memory->context, count * 12, 1);
    for (uint32_t i = 0; i < count; ++i) { buckets[i].key = 0; buckets[i].value = NULL; buckets[i].next = NULL; }
    table->buckets = buckets; table->count = 0; table->flags = 0;
    return table;
}
/* 0x00462740. New collisions follow the inline bucket. Duplicate keys and
 * null values are not rejected; even a null-valued insertion increments count. */
uint32_t thug_object_table_insert(ThugObjectLookupTable *table, const uint32_t *key, void *value, const ThugMemory *memory) {
    uint32_t name = *key, mask = (1u << (table->shift & 31)) - 1;
    ThugObjectLookupNode *bucket = table->buckets + (name & mask);
    if (bucket->value) {
        /* Original 5bc450 allocator, constant type argument zero. */
        ThugObjectLookupNode *node = thug_lookup_node_pool ? thug_pool_allocate(thug_lookup_node_pool)
            : memory->allocate(memory->context, 12, 1);
        node->key = 0; node->value = NULL; node->next = NULL;
        node->key = *key; node->value = value; node->next = bucket->next; bucket->next = node;
    } else { bucket->value = value; bucket->key = name; }
    ++table->count;
    return 1;
}
/* 0x005b80d0. Removing the inline bucket keeps its collision chain. */
void thug_object_table_remove(ThugObjectLookupTable *table, const uint32_t *key, const ThugMemory *memory) {
    if (!table->buckets) return;
    uint32_t mask = (1u << (table->shift & 31)) - 1;
    ThugObjectLookupNode *node = table->buckets + (*key & mask), *previous = NULL;
    while (node) {
        if (node->key == *key && node->value) {
            if (previous) {
                previous->next = node->next;
                /* Original 5bc4a0 allocator, constant type argument zero. */
                if (thug_lookup_node_pool) thug_pool_release(thug_lookup_node_pool, node);
                else memory->release(memory->context, node);
            } else { node->key = 0; node->value = NULL; }
            --table->count;
            return;
        }
        previous = node; node = node->next;
    }
}
