#ifndef THUG_COLLISION_SEGMENT_H
#define THUG_COLLISION_SEGMENT_H
#include "geometry.h"

typedef struct ThugCollisionInstance ThugCollisionInstance;
typedef struct ThugCollisionResult ThugCollisionResult;
typedef struct ThugCollisionScene ThugCollisionScene;

/* Recovered prefixes only. Other virtual methods are not implemented yet.
 * The PC's thiscall receiver becomes an explicit first C argument. */
typedef struct {
    uint32_t unknown_0, unknown_4;
    uint16_t (*surface_flags)(const ThugCollisionInstance *, uint32_t);
    uint16_t (*surface_metadata)(const ThugCollisionInstance *, uint32_t);
    void (*set_geometry)(ThugCollisionInstance *, const ThugCollisionObject *);
    uint32_t unknown_14_to_24[5];
    void *(*owner)(const ThugCollisionInstance *);
    uint32_t unknown_2c_to_30[2];
    uint8_t (*intersects)(const ThugCollisionInstance *, const ThugBounds *);
    uint8_t (*segment)(const ThugCollisionInstance *, const float *, const float *,
        ThugCollisionResult *, const ThugBounds *, ThugCollisionQuery *);
    uint32_t unknown_3c_to_4c[5];
    const ThugBounds *(*moving_bounds)(ThugCollisionInstance *);
    const ThugBounds *(*bounds)(const ThugCollisionInstance *);
} ThugCollisionMethods;

struct ThugCollisionInstance {
    const ThugCollisionMethods *methods;
    uint32_t checksum;
    uint16_t flags;
    uint8_t query_stamp, unknown_b;
    const ThugCollisionObject *geometry;
};

typedef struct {
    ThugCollisionInstance base;
    const uint8_t *large_face_radii;
    float cached_radius_scale;
} ThugStaticCollisionInstance;

typedef struct {
    float normal[4], point[4];
    uint32_t face;
} ThugCollisionHit;

struct ThugCollisionResult {
    ThugCollisionHit surface;
    float fraction;
    uint16_t excluded_flags, required_flags, surface_flags;
    uint8_t surface_metadata, padding_2f;
    const ThugCollisionInstance *instance;
    uint32_t checksum, unknown_38;
    void (*callback)(ThugCollisionResult *);
    uint32_t unknown_40, unknown_44;
    uint8_t hit, flag_40, padding_4a, padding_4b;
    const ThugCollisionScene *scene;
};

extern const ThugCollisionMethods thug_static_collision_methods;
extern uint8_t thug_collision_select_farthest;
ThugStaticCollisionInstance *thug_static_collision_initialize(ThugStaticCollisionInstance *instance);
void thug_collision_set_geometry(ThugCollisionInstance *instance, const ThugCollisionObject *object);
const uint8_t *thug_collision_bind_radii(ThugStaticCollisionInstance *instance,
    const uint8_t *radii, const ThugCollisionObject *object);
const ThugBounds *thug_static_collision_bounds(const ThugCollisionInstance *instance);
uint16_t thug_collision_surface_flags(const ThugCollisionInstance *instance, uint32_t face);
uint16_t thug_collision_surface_metadata(const ThugCollisionInstance *instance, uint32_t face);
uint8_t thug_static_collision_intersects(const ThugCollisionInstance *instance, const ThugBounds *bounds);
ThugCollisionResult *thug_collision_result_copy(ThugCollisionResult *destination,
    const ThugCollisionResult *source);
uint8_t thug_collision_select_hit(const float segment[8], const ThugCollisionInstance *instance,
    const ThugCollisionHit *hit, float fraction, ThugCollisionResult *result);
uint8_t thug_static_collision_segment(const ThugCollisionInstance *instance,
    const float segment[8], const float delta[4], ThugCollisionResult *result,
    const ThugBounds *bounds, ThugCollisionQuery *query_state);
#endif
