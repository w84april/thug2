#ifndef THUG_COLLISION_LOAD_H
#define THUG_COLLISION_LOAD_H
#include "scene.h"

/* Internal version-10 loader. The input is modified in place, once only.
 * Validate file sections, counts, trees and indices before calling this code.
 * Bounds must be initialized by the caller; the loader expands them.
 */
uint8_t thug_collision_load(uint32_t receiver, void *data, int32_t *count,
    ThugStaticCollisionInstance **instances, ThugCollisionObject **objects,
    ThugBounds *bounds, uint32_t unused, const ThugMemory *memory);
#endif
