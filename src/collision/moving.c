#include "moving.h"
#include "../core/matrix.h"
#include "../core/vector.h"
#include "../core/number.h"
#include <stddef.h>

_Static_assert(sizeof(ThugMovingCollisionInstance) == 0xd4, "Moving collision layout");
_Static_assert(offsetof(ThugMovingCollisionInstance, bounds) == 0xac, "Moving bounds offset");
_Static_assert(offsetof(ThugCollisionMethods, owner) == 0x28, "Owner virtual method offset");

const ThugCollisionMethods thug_moving_collision_methods = {
    .surface_flags = thug_collision_surface_flags,
    .surface_metadata = thug_collision_surface_metadata,
    .set_geometry = thug_moving_collision_set_geometry,
    .owner = thug_moving_collision_owner,
    .intersects = thug_moving_collision_intersects,
    .segment = thug_moving_collision_segment,
    .moving_bounds = thug_moving_collision_bounds
};

/* 0x00411780. The original requires nonnull geometry, even though checksum
 * assignment alone is guarded. Radius is measured from the local origin. */
void thug_moving_collision_set_geometry(ThugCollisionInstance *base, const ThugCollisionObject *object) {
    ThugMovingCollisionInstance *instance = (ThugMovingCollisionInstance *)base;
    base->geometry = object;
    if (object) base->checksum = object->checksum;
    instance->radius = 0;
    for (uint32_t i = 0; i < object->vertex_count; ++i) {
        float vertex[4];
        thug_collision_vertex(object, vertex, i);
        float radius = __builtin_sqrtf((vertex[0] * vertex[0] + vertex[1] * vertex[1]) + vertex[2] * vertex[2]);
        if (radius > instance->radius) instance->radius = radius;
    }
    instance->bounds_dirty = 1;
}

/* 0x00413000, including the base initialization at 0x00411fa0. C++ exception
 * registration is omitted. Uninitialized checksum/stamp/padding stay untouched. */
ThugMovingCollisionInstance *thug_moving_collision_initialize(ThugMovingCollisionInstance *instance,
    const ThugCollisionObject *object) {
    instance->base.flags = 0;
    instance->base.geometry = NULL;
    for (unsigned i = 0; i < 4; ++i) instance->position[i] = i == 3 ? 1.0f : 0.0f;
    instance->owner = NULL;
    for (unsigned i = 0; i < 16; ++i) {
        instance->orientation[i] = i % 5 == 0 ? 1.0f : 0.0f;
        instance->inverse[i] = i % 5 == 0 ? 1.0f : 0.0f;
    }
    instance->base.methods = &thug_moving_collision_methods;
    thug_bounds_reset(&instance->bounds);
    thug_moving_collision_set_geometry(&instance->base, object);
    instance->cached_radius_scale = object->face_radius_scale;
    instance->bounds_dirty = 1;
    return instance;
}

/* 0x00412f90. */
void thug_moving_collision_set_position(ThugMovingCollisionInstance *instance, const float position[4]) {
    for (unsigned i = 0; i < 4; ++i) instance->position[i] = position[i];
    instance->bounds_dirty = 1;
}

/* 0x00412070 (also reached through thunk 0x00412ff0). Only the first three
 * rows are replaced; the retained fourth row participates in the transpose.
 * Intended inputs are rotation matrices; this is not a general matrix inverse. */
float *thug_moving_collision_set_orientation(ThugMovingCollisionInstance *instance, const float orientation[16]) {
    for (unsigned i = 0; i < 12; ++i) instance->orientation[i] = orientation[i];
    for (unsigned row = 0; row < 4; ++row)
        for (unsigned column = 0; column < 4; ++column)
            instance->inverse[row * 4 + column] = instance->orientation[column * 4 + row];
    return instance->inverse;
}

/* 0x0040ae40 / 0x0040ae50. */
void thug_moving_collision_set_owner(ThugMovingCollisionInstance *instance, void *owner) { instance->owner = owner; }
void *thug_moving_collision_owner(const ThugCollisionInstance *instance) {
    return ((const ThugMovingCollisionInstance *)instance)->owner;
}

/* 0x0040b390. Does not clear the dirty flag itself. */
void thug_moving_collision_update_bounds(ThugMovingCollisionInstance *instance) {
    for (unsigned i = 0; i < 3; ++i) {
        instance->bounds.min[i] = instance->position[i] - instance->radius;
        instance->bounds.max[i] = instance->position[i] + instance->radius;
    }
    instance->bounds.min[3] = instance->bounds.max[3] = 1;
}

/* 0x00412fc0. The accessor refreshes the lazy bounds before clearing dirtiness. */
const ThugBounds *thug_moving_collision_bounds(ThugCollisionInstance *base) {
    ThugMovingCollisionInstance *instance = (ThugMovingCollisionInstance *)base;
    if (instance->bounds_dirty) {
        thug_moving_collision_update_bounds(instance);
        instance->bounds_dirty = 0;
    }
    return &instance->bounds;
}

/* 0x00411810. The virtual query lazily refreshes its receiver's bounds. */
uint8_t thug_moving_collision_intersects(const ThugCollisionInstance *base, const ThugBounds *bounds) {
    ThugMovingCollisionInstance *instance = (ThugMovingCollisionInstance *)base;
    if (instance->bounds_dirty) {
        thug_moving_collision_update_bounds(instance);
        instance->bounds_dirty = 0;
    }
    return thug_bounds_overlap(bounds, &instance->bounds);
}

/* 0x004122c0. Supports an identical source/destination. */
void thug_moving_collision_local_segment(const ThugMovingCollisionInstance *instance,
    const float input[8], float output[8]) {
    for (unsigned i = 0; i < 8; ++i) output[i] = input[i];
    for (unsigned i = 0; i < 8; ++i) output[i] -= instance->position[i % 4];
    thug_matrix_rotate_vector(instance->inverse, output, output);
    thug_matrix_rotate_vector(instance->inverse, output + 4, output + 4);
}

/* 0x00414460. Caller-supplied delta and bounds are unused: local-space values
 * are recomputed. Unlike static collision, large faces bypass radius rejection. */
uint8_t thug_moving_collision_segment(const ThugCollisionInstance *base, const float segment[8],
    const float delta_unused[4], ThugCollisionResult *result, const ThugBounds *bounds_unused,
    ThugCollisionQuery *query_state) {
    (void)delta_unused; (void)bounds_unused;
    const ThugMovingCollisionInstance *instance = (const ThugMovingCollisionInstance *)base;
    float local[8], delta[4];
    thug_moving_collision_local_segment(instance, segment, local);
    for (unsigned i = 0; i < 4; ++i) delta[i] = local[i + 4] - local[i];
    ThugBounds bounds;
    thug_bounds_from_point(&bounds, local); thug_bounds_expand(&bounds, local + 4);
    const ThugCollisionObject *object = base->geometry;
    uint32_t threshold = 0;
    if (object->small_faces) {
        float normal[4] = { delta[0], delta[1], delta[2], delta[3] };
        thug_vector_normalize(normal);
        float dx = object->bounds.min[0] - local[0], dy = object->bounds.min[1] - local[1];
        float dz = object->bounds.min[2] - local[2];
        float projection = (dx * normal[0] + dz * normal[2]) + dy * normal[1];
        dx -= normal[0] * projection; dy -= normal[1] * projection; dz -= normal[2] * projection;
        float distance = __builtin_sqrtf((dx * dx + dz * dz) + dy * dy);
        threshold = thug_truncate_low_word(distance * object->face_radius_scale);
        if (threshold > 255) return 0;
    }
    uint16_t storage[2048]; uint32_t count;
    const uint16_t *faces = thug_collision_query(object, &bounds, &count, storage, 0x800, query_state);
    uint8_t found = 0;
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t face = faces[i]; object = base->geometry;
        const uint8_t *record = (const uint8_t *)object->faces + face * (object->small_faces ? 8 : 10);
        if (object->small_faces && threshold > record[7]) continue;
        float a[4], b[4], c[4], fraction;
        float *vertices[3] = { a, b, c };
        for (unsigned corner = 0; corner < 3; ++corner) {
            uint32_t vertex = object->small_faces ? record[4 + corner] : ((const uint16_t *)(record + 4))[corner];
            thug_collision_vertex_into(object, vertex, vertices[corner]);
        }
        if (!thug_collision_triangle(local, delta, a, b, c, &fraction)) continue;
        float ex = b[0] - a[0], ey = b[1] - a[1], ez = b[2] - a[2];
        float fx = c[0] - a[0], fy = c[1] - a[1], fz = c[2] - a[2];
        float nx = fz * ey - fy * ez, ny = ez * fx - fz * ex, nz = fy * ex - ey * fx;
        float length = __builtin_sqrtf((nx * nx + nz * nz) + ny * ny);
        if (length > 0) { float inverse = 1.0f / length; nx *= inverse; ny *= inverse; nz *= inverse; }
        const float *m = instance->orientation;
        ThugCollisionHit hit;
        hit.face = face;
        for (unsigned axis = 0; axis < 3; ++axis)
            hit.point[axis] = ((a[2] * m[8 + axis] + a[1] * m[4 + axis]) + a[0] * m[axis]) + instance->position[axis];
        hit.point[3] = a[3] + instance->position[3];
        hit.normal[0] = (nz * m[8] + ny * m[4]) + nx * m[0];
        hit.normal[1] = (nx * m[1] + nz * m[9]) + ny * m[5];
        hit.normal[2] = (nx * m[2] + nz * m[10]) + ny * m[6];
        hit.normal[3] = 0;
        if (thug_collision_select_hit(segment, base, &hit, fraction, result)) found = 1;
    }
    return found;
}

ThugMovingCollisionNode *thug_moving_collision_list; /* 0x00691984, sentinel object == -1. */

/* 0x004118c0. Preserve an earlier static hit's fraction. Cached entries start
 * after the static entries and bypass the live list's flags and lazy bounds.
 * The returned owner is the last object whose segment method accepted a hit. */
void *thug_moving_scene_segment(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache, ThugCollisionQuery *query_state) {
    result->callback = callback;
    void *found = NULL;
    if (!result->hit) result->fraction = thug_collision_select_farthest ? -0.01f : 1.01f;
    ThugBounds bounds;
    thug_bounds_from_point(&bounds, segment); thug_bounds_expand(&bounds, segment + 4);
    uint8_t use_cache = cache && thug_bounds_contains(&cache->bounds, &bounds);
    float point[4];
    for (unsigned i = 0; i < 3; ++i) point[i] = bounds.max[i] + 0.5f;
    point[3] = bounds.max[3]; thug_bounds_expand(&bounds, point);
    for (unsigned i = 0; i < 3; ++i) point[i] = bounds.min[i] - 0.5f;
    point[3] = bounds.min[3]; thug_bounds_expand(&bounds, point);
    float delta[4];
    for (unsigned i = 0; i < 4; ++i) delta[i] = segment[i + 4] - segment[i];
    if (use_cache) {
        int32_t count = cache->moving_count;
        const ThugCachedCollision *entry = cache->objects + cache->static_count;
        for (int32_t i = 0; i < count; ++i, ++entry) {
            if (entry->bounds && thug_bounds_overlap(&bounds, entry->bounds)) {
                ThugCollisionInstance *object = entry->object;
                result->unknown_44 = (uintptr_t)object->methods->owner(object);
                if (object->methods->segment(object, segment, delta, result, &bounds, query_state))
                    found = object->methods->owner(object);
                result->unknown_44 = 0;
            }
        }
    } else {
        ThugMovingCollisionNode *node = thug_moving_collision_list;
        while ((uintptr_t)node->object != UINT32_MAX && node) {
            ThugCollisionInstance *object = node->object;
            if (object && !(object->flags & 6) && object->methods->intersects(object, &bounds)) {
                result->unknown_44 = (uintptr_t)object->methods->owner(object);
                if (object->methods->segment(object, segment, delta, result, &bounds, query_state))
                    found = object->methods->owner(object);
                result->unknown_44 = 0;
            }
            node = node->next;
        }
    }
    return found;
}

/* 0x00411ae0. Like the static wrapper, resets the selection mode to zero. */
void *thug_moving_scene_segment_farthest(const float segment[8], ThugCollisionResult *result,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *cache, ThugCollisionQuery *query_state) {
    thug_collision_select_farthest = 1;
    void *found = thug_moving_scene_segment(segment, result, callback, cache, query_state);
    thug_collision_select_farthest = 0;
    return found;
}
