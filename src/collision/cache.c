#include "moving.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(sizeof(ThugCollisionCache) == 0xfcc, "Collision cache size");
_Static_assert(offsetof(ThugCollisionMethods, moving_bounds) == 0x50, "Moving bounds method");
ThugCollisionCache *thug_collision_cache_registry[8]; /* 0x006918ec */
uint32_t thug_collision_cache_mask; /* 0x0069190c */

/* 0x00402600. Forward word copies retain partial overlap and raw float bits. */
float *thug_collision_segment_copy(float out[8], const float start[4], const float end[4]) {
    for (unsigned i = 0; i < 4; ++i) __builtin_memcpy(out+i,start+i,4);
    for (unsigned i = 0; i < 4; ++i) __builtin_memcpy(out+i+4,end+i,4);
    return out;
}
/* 0x0040aa00 / 0x0040aa40. Duplicate registrations occupy separate slots.
 * A full registry does nothing; removal clears the first live bit only. */
void thug_collision_cache_register(ThugCollisionCache *cache) {
    uint32_t mask = thug_collision_cache_mask;
    for (unsigned i = 0; i < 8; ++i) if (!(mask & (1u << i))) {
        thug_collision_cache_registry[i] = cache;
        thug_collision_cache_mask = mask | (1u << i);
        return;
    }
}
void thug_collision_cache_unregister(ThugCollisionCache *cache) {
    uint32_t mask = thug_collision_cache_mask;
    for (unsigned i = 0; i < 8; ++i) if ((mask & (1u << i)) && thug_collision_cache_registry[i] == cache) {
        thug_collision_cache_mask = mask & ~(1u << i); return;
    }
}
/* 0x0040ab50 / 0x0040ab40. The inactive registry slot retains its pointer. */
ThugCollisionCache *thug_collision_cache_initialize(ThugCollisionCache *cache) {
    thug_bounds_reset(&cache->bounds);
    thug_collision_cache_register(cache);
    thug_bounds_reset(&cache->bounds);
    cache->count = cache->static_count = cache->moving_count = 0;
    return cache;
}
void thug_collision_cache_destroy(ThugCollisionCache *cache) { thug_collision_cache_unregister(cache); }

/* 0x0040aba0. A scene miss leaves reset bounds/counts and old entry storage.
 * Static candidates precede moving ones; bounds come from concrete virtuals. */
void thug_collision_cache_build(ThugCollisionCache *cache, const ThugBounds *requested) {
    thug_bounds_reset(&cache->bounds);
    cache->count = cache->static_count = cache->moving_count = 0;
    float segment[8]; thug_collision_segment_copy(segment,requested->min,requested->max);
    ThugCollisionGrid **grids = thug_collision_select_scenes(segment);
    if (!grids) return;
    thug_collision_segment_copy(cache->bounds.min,requested->min,requested->max);
    ThugBounds expanded; thug_bounds_reset(&expanded);
    float point[4]; point[3] = requested->max[3];
    for (unsigned i = 0; i < 3; ++i) point[i] = (float)thug_platform_round_x87_single((double)requested->max[i]+0.5);
    thug_bounds_expand(&expanded,point); point[3] = requested->min[3];
    for (unsigned i = 0; i < 3; ++i) point[i] = (float)thug_platform_round_x87_single((double)requested->min[i]-0.5);
    thug_bounds_expand(&expanded,point);
    while (*grids) {
        ThugCollisionInstance **objects = thug_collision_grid_query(*grids++,segment,NULL);
        for (; *objects; ++objects) {
            ThugCollisionInstance *object = *objects;
            if (object->methods->intersects(object,&expanded)) {
                const ThugBounds *bounds = object->methods->bounds(object);
                cache->objects[cache->count].bounds = bounds;
                cache->objects[cache->count].object = object;
                ++cache->count; ++cache->static_count;
            }
        }
    }
    ThugMovingCollisionNode *node = thug_moving_collision_list;
    while ((uintptr_t)node->object != UINT32_MAX && node) {
        ThugCollisionInstance *object = node->object;
        if (object && !(object->flags & 6) && object->methods->intersects(object,&expanded)) {
            const ThugBounds *bounds = object->methods->moving_bounds(object);
            cache->objects[cache->count].bounds = bounds;
            cache->objects[cache->count].object = object;
            ++cache->count; ++cache->moving_count;
        }
        node = node->next;
    }
}
