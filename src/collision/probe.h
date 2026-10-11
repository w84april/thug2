#ifndef THUG_COLLISION_PROBE_H
#define THUG_COLLISION_PROBE_H
#include "moving.h"
#include "../core/memory.h"

typedef struct ThugObjectReference ThugObjectReference;
typedef struct {
    uint32_t unknown_0;
    ThugObjectReference *references;
    uint32_t unknown_8_to_10[3], id;
} ThugReferencedObject;
struct ThugObjectReference {
    ThugReferencedObject *object;
    ThugObjectReference *previous, *next;
};
typedef struct ThugReferenceTarget ThugReferenceTarget;
typedef struct {
    ThugReferenceTarget *(*dispose)(ThugReferenceTarget *, uint32_t flags, const ThugMemory *);
} ThugReferenceTargetMethods;
/* The eight-byte referenced base is also embedded at script offset 0xec. */
struct ThugReferenceTarget {
    const ThugReferenceTargetMethods *methods;
    ThugObjectReference *references;
};
extern const ThugReferenceTargetMethods thug_reference_target_methods;
ThugReferenceTarget *thug_reference_target_initialize(ThugReferenceTarget *);
void thug_object_references_clear(ThugReferenceTarget *);
void thug_reference_target_destroy(ThugReferenceTarget *);
ThugReferenceTarget *thug_reference_target_delete(ThugReferenceTarget *, uint32_t flags, const ThugMemory *);
void thug_object_reference_link(ThugReferencedObject *, ThugObjectReference *);
void thug_object_reference_unlink(ThugReferencedObject *, ThugObjectReference *);
ThugObjectReference *thug_object_reference_initialize(ThugObjectReference *);
void thug_object_reference_destroy(ThugObjectReference *);
ThugObjectReference *thug_object_reference_assign(ThugObjectReference *, ThugReferencedObject *);
ThugObjectReference *thug_object_reference_assign_reference(ThugObjectReference *, const ThugObjectReference *);

typedef struct ThugCollisionProbe {
    float segment[8];
    void (*callback)(struct ThugCollisionProbe *);
    ThugCollisionResult result;
    float fraction, point[4], normal[4];
    ThugObjectReference moving_object;
    uint32_t moving_object_id, unknown_a8;
    const ThugCollisionCache *cache;
} ThugCollisionProbe;
extern const ThugCollisionCache *thug_collision_default_cache;
ThugCollisionProbe *thug_collision_probe_initialize(ThugCollisionProbe *);
void thug_collision_probe_release(ThugCollisionProbe *);
ThugCollisionProbe *thug_collision_probe_assign(ThugCollisionProbe *, const ThugCollisionProbe *);
ThugCollisionProbe *thug_collision_probe_copy_initialize(ThugCollisionProbe *, const ThugCollisionProbe *);
ThugCollisionProbe *thug_collision_probe_from_points(ThugCollisionProbe *, const float start[4], const float end[4]);
void thug_collision_probe_set_points(ThugCollisionProbe *, const float start[4], const float end[4]);
void thug_collision_probe_set_flags(ThugCollisionProbe *, uint16_t excluded, uint16_t required);
ThugReferencedObject *thug_collision_probe_event_object(const ThugCollisionProbe *);
uint8_t thug_collision_probe_has_moving_object(ThugCollisionProbe *);
ThugReferencedObject *thug_collision_probe_moving_object(const ThugCollisionProbe *);
void thug_collision_probe_callback(ThugCollisionResult *);
uint8_t thug_collision_probe_query(ThugCollisionProbe *, uint8_t check_moving,
    uint8_t farthest, ThugCollisionQuery *);
void thug_collision_probe_reverse(ThugCollisionProbe *);
#endif
