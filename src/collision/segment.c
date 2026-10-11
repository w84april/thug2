/* Recovered from the modified PC executable pinned in tools/specimen.py.
 * Names and types are analyst-assigned. Internal routines require valid data.
 */
#include "segment.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>

_Static_assert(sizeof(ThugCollisionHit) == 36, "Collision hit layout");
_Static_assert(sizeof(ThugCollisionResult) == 80, "Collision result layout");
_Static_assert(offsetof(ThugCollisionResult, callback) == 0x3c, "Hit callback offset");
_Static_assert(offsetof(ThugCollisionInstance, geometry) == 0xc, "Geometry pointer offset");
_Static_assert(sizeof(ThugCollisionInstance) == 0x10, "Common collision instance size");
_Static_assert(sizeof(ThugStaticCollisionInstance) == 0x18, "Static collision instance size");
_Static_assert(offsetof(ThugCollisionMethods, bounds) == 0x54, "Bounds virtual method offset");

/* 0x00691910: nonzero selects the farthest hit instead of the nearest. */
uint8_t thug_collision_select_farthest;

/* Known prefix of the static instance's vtable at 0x00645c18. */
const ThugCollisionMethods thug_static_collision_methods = {
    .surface_flags = thug_collision_surface_flags,
    .surface_metadata = thug_collision_surface_metadata,
    .set_geometry = thug_collision_set_geometry,
    .intersects = thug_static_collision_intersects,
    .segment = thug_static_collision_segment,
    .bounds = thug_static_collision_bounds
};

/* 0x00412730: checksum, query_stamp and unknown_b are intentionally untouched. */
ThugStaticCollisionInstance *thug_static_collision_initialize(ThugStaticCollisionInstance *instance) {
    instance->base.flags = 0;
    instance->base.geometry = NULL;
    instance->base.methods = &thug_static_collision_methods;
    instance->large_face_radii = NULL;
    instance->cached_radius_scale = 0.0f;
    return instance;
}

/* 0x0040b370: clearing the geometry preserves the prior checksum. */
void thug_collision_set_geometry(ThugCollisionInstance *instance, const ThugCollisionObject *object) {
    instance->geometry = object;
    if (object) instance->checksum = object->checksum;
}

/* 0x00410bc0: small-face radius bytes are embedded, leaving this pointer alone. */
const uint8_t *thug_collision_bind_radii(ThugStaticCollisionInstance *instance,
    const uint8_t *radii, const ThugCollisionObject *object) {
    instance->cached_radius_scale = object->face_radius_scale;
    if (object->small_faces) return radii;
    instance->large_face_radii = radii;
    return radii + object->face_count;
}

/* 0x00412750. */
const ThugBounds *thug_static_collision_bounds(const ThugCollisionInstance *instance) {
    return &instance->geometry->bounds;
}

/* 0x00410c70. */
uint8_t thug_static_collision_intersects(const ThugCollisionInstance *instance, const ThugBounds *bounds) {
    return thug_bounds_overlap(bounds, &instance->geometry->bounds);
}

/* 0x00410bf0. */
uint16_t thug_collision_surface_flags(const ThugCollisionInstance *instance, uint32_t face) {
    const ThugCollisionObject *object = instance->geometry;
    const uint8_t *bytes = object->faces;
    return *(const uint16_t *)(bytes + face * (object->small_faces ? 8 : 10));
}

/* 0x00411750: returns a word, although hit selection retains only its low byte. */
uint16_t thug_collision_surface_metadata(const ThugCollisionInstance *instance, uint32_t face) {
    const ThugCollisionObject *object = instance->geometry;
    const uint8_t *bytes = object->faces;
    return *(const uint16_t *)(bytes + face * (object->small_faces ? 8 : 10) + 2);
}

/* 0x004f8160: copies fields, leaving three padding bytes unchanged. Like the
 * original C++ assignment, use distinct objects or self-assignment, not partial
 * overlapping objects. Byte access retains unknown fields and float payloads. */
ThugCollisionResult *thug_collision_result_copy(ThugCollisionResult *destination,
    const ThugCollisionResult *source) {
    uint8_t *out = (uint8_t *)destination;
    const uint8_t *in = (const uint8_t *)source;
    for (unsigned i = 0; i < 0x2f; ++i) out[i] = in[i];
    for (unsigned i = 0x30; i < 0x4a; ++i) out[i] = in[i];
    for (unsigned i = 0x4c; i < 0x50; ++i) out[i] = in[i];
    return destination;
}

/* 0x004131f0. A nonselected hit still reaches the callback when its flags pass.
 * Its temporary result is then rolled back, excluding the padding bytes. */
uint8_t thug_collision_select_hit(const float segment[8], const ThugCollisionInstance *instance,
    const ThugCollisionHit *hit, float fraction, ThugCollisionResult *result) {
    ThugCollisionResult previous;
    uint8_t selected = thug_collision_select_farthest
        ? fraction >= result->fraction : fraction <= result->fraction;
    uint8_t accepted = 0;
    if (!selected) thug_collision_result_copy(&previous, result);
    uint32_t face = hit->face;
    uint16_t flags = instance->methods->surface_flags(instance, face);
    if (!(flags & result->excluded_flags) && !((uint16_t)~flags & result->required_flags)) {
        result->hit = 1;
        result->surface = *hit;
        result->fraction = fraction;
        result->surface_flags = flags;
        result->surface_metadata = (uint8_t)instance->methods->surface_metadata(instance, face);
        result->instance = instance;
        result->flag_40 = flags & 0x40;
        result->checksum = instance->checksum;
        for (unsigned i = 0; i < 3; ++i)
            result->surface.point[i] = (segment[i + 4] - segment[i]) * fraction + segment[i];
        result->surface.point[3] = 1.0f;
        if (result->callback) result->callback(result);
        accepted = 1;
    }
    if (!selected) {
        thug_collision_result_copy(result, &previous);
        return 0;
    }
    return accepted;
}

/* 0x00413b50: static collision instance's segment query. The original local
 * candidate buffer holds 2048 entries; callers must respect that object limit.
 * The original BSP globals have been lifted into query_state, as in tree.c. */
uint8_t thug_static_collision_segment(const ThugCollisionInstance *instance,
    const float segment[8], const float delta[4], ThugCollisionResult *result,
    const ThugBounds *bounds, ThugCollisionQuery *query_state) {
    /* PC24 retains the exponent range until each actual FSTP float. X/Y
     * normalized coordinates stay on the x87 stack; Z is stored to float. */
#define R24 thug_platform_round_x87_single
    double nx = delta[0], ny = delta[1];
    float nz = delta[2];
    double length = R24(__builtin_sqrt(R24(R24(R24((double)nz*nz) + R24(ny*ny)) + R24(nx*nx))));
    if (length > 0.0f) {
        double inverse = R24(1.0 / length);
        nx = R24(nx*inverse); ny = R24(ny*inverse); nz = (float)R24((double)nz*inverse);
    }
    const ThugCollisionObject *object = instance->geometry;
    float dx = object->bounds.min[0] - segment[0];
    float dy = object->bounds.min[1] - segment[1];
    double dz = R24((double)object->bounds.min[2] - segment[2]);
    float projection = (float)R24(R24(R24(dz*nz) + R24(dy*ny)) + R24(dx*nx));
    dx -= (float)R24(nx*projection);
    dy = (float)R24((double)dy-R24(ny*projection));
    dz = R24((double)(float)dz-R24((double)nz*projection));
    double distance = R24(__builtin_sqrt(R24(R24(R24(dz*dz) + R24((double)dy*dy)) + R24((double)dx*dx))));
    uint32_t threshold = thug_truncate_double_low_word(R24(distance*object->face_radius_scale));
#undef R24
    if (threshold > 255) return 0;
    uint16_t storage[2048];
    uint32_t count;
    const uint16_t *faces = thug_collision_query(object, bounds, &count, storage, 0x800, query_state);
    uint8_t found = 0;
    for (uint32_t i = 0; i < count; ++i) {
        uint32_t face = faces[i];
        /* Reload the instance's geometry, as the original does after callbacks. */
        object = instance->geometry;
        const uint8_t *record = (const uint8_t *)object->faces + face * (object->small_faces ? 8 : 10);
        uint32_t radius = object->small_faces ? record[7]
            : ((const ThugStaticCollisionInstance *)instance)->large_face_radii[face];
        if (threshold > radius) continue;
        float a[4], b[4], c[4], fraction;
        float *vertices[3] = { a, b, c };
        for (unsigned corner = 0; corner < 3; ++corner) {
            uint32_t vertex = object->small_faces ? record[4 + corner]
                : ((const uint16_t *)(record + 4))[corner];
            thug_collision_vertex_into(object, vertex, vertices[corner]);
        }
        if (!thug_collision_triangle(segment, delta, a, b, c, &fraction)) continue;
        float ex = b[0] - a[0], ey = b[1] - a[1], ez = b[2] - a[2];
        float fx = c[0] - a[0], fy = c[1] - a[1], fz = c[2] - a[2];
        ThugCollisionHit hit = {
            { fz * ey - fy * ez, ez * fx - fz * ex, fy * ex - ey * fx, 0 },
            { a[0], a[1], a[2], a[3] }, face
        };
        thug_vector_normalize(hit.normal);
        if (thug_collision_select_hit(segment, instance, &hit, fraction, result)) found = 1;
    }
    return found;
}
