#include "probe.h"
#include "../core/vector.h"
#include <stddef.h>
/* 0x0042b580 and 0x00416dd0. An unattached reference's links are not reset
 * by destruction. Constructors require a fresh, unlinked reference. */
ThugObjectReference *thug_object_reference_initialize(ThugObjectReference *reference) {
    reference->previous = reference->next = NULL; reference->object = NULL;
    return reference;
}
void thug_object_reference_destroy(ThugObjectReference *reference) {
    if (reference->object) {
        thug_object_reference_unlink(reference->object, reference); reference->object = NULL;
    }
}

_Static_assert(sizeof(ThugCollisionProbe) == 0xb0, "Probe layout");
_Static_assert(offsetof(ThugCollisionProbe, moving_object) == 0x98, "Probe reference offset");
_Static_assert(offsetof(ThugCollisionProbe, result) == 0x24, "Probe result offset");

/* 0x004f8200. A copy constructor requires fresh, unlinked destination storage.
 * Result padding is retained and only the new moving reference is linked. */
ThugCollisionProbe *thug_collision_probe_copy_initialize(ThugCollisionProbe *destination,
    const ThugCollisionProbe *source) {
    thug_vector_copy(destination->segment,source->segment);
    thug_vector_copy(destination->segment+4,source->segment+4);
    destination->callback=source->callback;
    thug_collision_result_copy(&destination->result,&source->result);
    __builtin_memcpy(&destination->fraction,&source->fraction,4);
    thug_vector_copy(destination->point,source->point);
    thug_vector_copy(destination->normal,source->normal);
    destination->moving_object.previous=destination->moving_object.next=NULL;
    destination->moving_object.object=source->moving_object.object;
    if(destination->moving_object.object)
        thug_object_reference_link(destination->moving_object.object,&destination->moving_object);
    destination->moving_object_id=source->moving_object_id;
    destination->unknown_a8=source->unknown_a8;
    destination->cache=source->cache;
    return destination;
}

/* 0x0043a930. Preserve result padding and the original forward-copy order.
 * Self-assignment detaches its own reference before reading the source owner. */
ThugCollisionProbe *thug_collision_probe_assign(ThugCollisionProbe *destination, const ThugCollisionProbe *source) {
    thug_vector_copy(destination->segment, source->segment);
    thug_vector_copy(destination->segment+4, source->segment+4);
    destination->callback = source->callback;
    thug_collision_result_copy(&destination->result, &source->result);
    __builtin_memcpy(&destination->fraction, &source->fraction, 4);
    thug_vector_copy(destination->point, source->point);
    thug_vector_copy(destination->normal, source->normal);
    if (destination->moving_object.object) {
        thug_object_reference_unlink(destination->moving_object.object, &destination->moving_object);
        destination->moving_object.object = NULL;
    }
    destination->moving_object.object = source->moving_object.object;
    if (destination->moving_object.object)
        thug_object_reference_link(destination->moving_object.object, &destination->moving_object);
    destination->moving_object_id = source->moving_object_id;
    destination->unknown_a8 = source->unknown_a8;
    destination->cache = source->cache;
    return destination;
}

const ThugCollisionCache *thug_collision_default_cache; /* 0x00691974. */

/* 0x00417140. During a moving collision callback, this field contains its owner.
 * It is separate from the persistent reference exposed by 0x00417240. */
ThugReferencedObject *thug_collision_probe_event_object(const ThugCollisionProbe *probe) {
    return (ThugReferencedObject *)(uintptr_t)probe->result.unknown_44;
}

/* 0x00417210. Clear the stale identity only when the reference has gone away.
 * With neither a reference nor an old moving identity, the checksum persists. */
uint8_t thug_collision_probe_has_moving_object(ThugCollisionProbe *probe) {
    if (probe->moving_object.object) return 1;
    if (probe->moving_object_id) {
        probe->moving_object_id = 0;
        probe->result.checksum = 0;
    }
    return 0;
}

/* 0x00417240. */
ThugReferencedObject *thug_collision_probe_moving_object(const ThugCollisionProbe *probe) {
    return probe->moving_object.object;
}

/* 0x0041c350. Release and clear an attached moving-object reference. A null
 * object leaves the remaining reference bytes alone. Other probe bytes persist. */
void thug_collision_probe_release(ThugCollisionProbe *probe) {
    if (probe->moving_object.object) {
        thug_object_reference_unlink(probe->moving_object.object, &probe->moving_object);
        probe->moving_object.object = NULL;
    }
}

/* 0x004170f0. */
void thug_collision_probe_set_flags(ThugCollisionProbe *probe, uint16_t excluded, uint16_t required) {
    probe->result.excluded_flags = excluded;
    probe->result.required_flags = required;
}

static void initialize_reference(ThugCollisionProbe *probe) {
    probe->moving_object.previous = probe->moving_object.next = NULL;
    probe->moving_object.object = NULL;
}
static void initialize_fields(ThugCollisionProbe *probe) {
    probe->result.required_flags = 0;
    probe->callback = NULL; probe->cache = NULL;
    probe->result.excluded_flags = 0x10;
    for (unsigned i = 0; i < 4; ++i) {
        probe->result.surface.normal[i] = i == 3 ? 1.0f : 0.0f;
        probe->result.surface.point[i] = i == 3 ? 1.0f : 0.0f;
    }
}

/* 0x00417760. Other result and public output fields remain uninitialized. */
ThugCollisionProbe *thug_collision_probe_initialize(ThugCollisionProbe *probe) {
    initialize_reference(probe); initialize_fields(probe); return probe;
}

/* 0x004171d0. */
void thug_collision_probe_set_points(ThugCollisionProbe *probe, const float start[4], const float end[4]) {
    for (unsigned i = 0; i < 4; ++i) probe->segment[i] = start[i];
    for (unsigned i = 0; i < 4; ++i) probe->segment[i + 4] = end[i];
}

/* 0x00417250. A constructor, not a reset for an already linked probe. */
ThugCollisionProbe *thug_collision_probe_from_points(ThugCollisionProbe *probe, const float start[4], const float end[4]) {
    initialize_reference(probe);
    thug_collision_probe_set_points(probe, start, end);
    initialize_fields(probe); return probe;
}

/* 0x004637c0. Caller sets object and supplies an unlinked reference. */
void thug_object_reference_link(ThugReferencedObject *object, ThugObjectReference *reference) {
    reference->next = object->references;
    if (object->references) object->references->previous = reference;
    object->references = reference;
}

/* 0x004637e0. Does not clear the reference's object pointer. */
void thug_object_reference_unlink(ThugReferencedObject *object, ThugObjectReference *reference) {
    if (reference->previous) reference->previous->next = reference->next;
    else object->references = reference->next;
    if (reference->next) reference->next->previous = reference->previous;
    reference->previous = reference->next = NULL;
}

const ThugReferenceTargetMethods thug_reference_target_methods = { thug_reference_target_delete };
/* 0x004637b0. */
ThugReferenceTarget *thug_reference_target_initialize(ThugReferenceTarget *target) {
    target->methods = &thug_reference_target_methods;
    target->references = NULL;
    return target;
}
/* 0x0041d1d0. The object argument is captured before the old link is removed. */
ThugObjectReference *thug_object_reference_assign(ThugObjectReference *out, ThugReferencedObject *object) {
    if (out->object) { thug_object_reference_unlink(out->object,out); out->object = NULL; }
    out->object = object;
    if (object) thug_object_reference_link(object,out);
    return out;
}
/* 0x004a8f60. Read the source after clearing the old destination. Self-assignment
 * therefore clears a live reference, just as in the original. */
ThugObjectReference *thug_object_reference_assign_reference(ThugObjectReference *out, const ThugObjectReference *source) {
    if (out->object) { thug_object_reference_unlink(out->object,out); out->object = NULL; }
    out->object = source->object;
    if (out->object) thug_object_reference_link(out->object,out);
    return out;
}
/* 0x00463820. Capture next before unlinking. Already unowned references retain
 * their links; the target head changes only through an owned node's unlink. */
void thug_object_references_clear(ThugReferenceTarget *target) {
    ThugObjectReference *reference = target->references;
    while (reference) {
        ThugObjectReference *next = reference->next;
        if (reference->object) {
            thug_object_reference_unlink(reference->object, reference);
            reference->object = NULL;
        }
        reference->object = NULL;
        reference = next;
    }
}
/* 0x00463870, 0x00463880. The deleting destructor uses the generic heap. */
void thug_reference_target_destroy(ThugReferenceTarget *target) {
    target->methods = &thug_reference_target_methods;
    thug_object_references_clear(target);
}
ThugReferenceTarget *thug_reference_target_delete(ThugReferenceTarget *target, uint32_t flags, const ThugMemory *memory) {
    thug_reference_target_destroy(target);
    if (flags & 1) memory->release(memory->context, target);
    return target;
}

/* 0x00417110, the bridge passed to scene queries. Resolve the current user
 * callback on each hit, as in the original tail call. */
void thug_collision_probe_callback(ThugCollisionResult *result) {
    ThugCollisionProbe *probe = (ThugCollisionProbe *)(uintptr_t)result->unknown_40;
    probe->callback(probe);
}

/* 0x004172f0. Snapshot the segment and cache before callbacks can modify the
 * probe. The previous moving-object reference is removed even on a miss. */
uint8_t thug_collision_probe_query(ThugCollisionProbe *probe, uint8_t check_moving,
    uint8_t farthest, ThugCollisionQuery *query_state) {
    float segment[8];
    for (unsigned i = 0; i < 8; ++i) segment[i] = probe->segment[i];
    probe->result.unknown_40 = (uintptr_t)probe;
    probe->result.hit = probe->result.flag_40 = 0;
    probe->result.unknown_38 = probe->result.unknown_44 = 0;
    void (*callback)(ThugCollisionResult *) = probe->callback ? thug_collision_probe_callback : NULL;
    const ThugCollisionCache *cache = probe->cache ? probe->cache : thug_collision_default_cache;
    ThugObjectReference *reference = &probe->moving_object;
    if (reference->object) {
        thug_object_reference_unlink(reference->object, reference);
        reference->object = NULL;
    }
    reference->object = NULL;
    probe->moving_object_id = 0;
    uint8_t found = farthest
        ? thug_collision_scene_segment_farthest(segment, &probe->result, callback, cache, query_state)
        : thug_collision_scene_segment(segment, &probe->result, callback, cache, query_state);
    if (check_moving) {
        ThugReferencedObject *object = farthest
            ? thug_moving_scene_segment_farthest(segment, &probe->result, callback, cache, query_state)
            : thug_moving_scene_segment(segment, &probe->result, callback, cache, query_state);
        if (reference->object) {
            thug_object_reference_unlink(reference->object, reference);
            reference->object = NULL;
        }
        reference->object = object;
        if (object) thug_object_reference_link(object, reference);
        if (reference->object) probe->moving_object_id = reference->object->id;
    }
    probe->fraction = probe->result.fraction;
    for (unsigned i = 0; i < 4; ++i) {
        probe->point[i] = probe->result.surface.point[i];
        probe->normal[i] = probe->result.surface.normal[i];
    }
    return found || reference->object;
}

static float probe_quiet(float value) {
    uint32_t bits;__builtin_memcpy(&bits,&value,4);
    if((bits&0x7f800000)==0x7f800000&&(bits&0x7fffff))bits|=0x400000;
    __builtin_memcpy(&value,&bits,4);return value;
}
/* 0057c210. Reverse the segment, retaining all unrelated probe fields.
 * Only the new start's X/Y travel through x87 loads/stores. */
void thug_collision_probe_reverse(ThugCollisionProbe *probe) {
    float end[4];__builtin_memcpy(end,probe->segment+4,16);
    __builtin_memcpy(probe->segment+4,probe->segment,16);
    end[0]=probe_quiet(end[0]);end[1]=probe_quiet(end[1]);
    __builtin_memcpy(probe->segment,end,16);
}
