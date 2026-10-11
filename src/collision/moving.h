#ifndef THUG_COLLISION_MOVING_H
#define THUG_COLLISION_MOVING_H
#include "scene.h"

/* Rigid moving collision class, vtable 0x00645ce0. The geometry and its BSP
 * remain in local coordinates; broad-phase bounds enclose a sphere. */
typedef struct {
    ThugCollisionInstance base;
    float position[4], orientation[16], inverse[16];
    void *owner;
    float radius;
    uint8_t bounds_dirty, padding_a9[3];
    ThugBounds bounds;
    uint32_t unknown_cc;
    float cached_radius_scale;
} ThugMovingCollisionInstance;

extern const ThugCollisionMethods thug_moving_collision_methods;
ThugMovingCollisionInstance *thug_moving_collision_initialize(ThugMovingCollisionInstance *, const ThugCollisionObject *);
void thug_moving_collision_set_geometry(ThugCollisionInstance *, const ThugCollisionObject *);
void thug_moving_collision_set_position(ThugMovingCollisionInstance *, const float position[4]);
float *thug_moving_collision_set_orientation(ThugMovingCollisionInstance *, const float orientation[16]);
void thug_moving_collision_set_owner(ThugMovingCollisionInstance *, void *);
void *thug_moving_collision_owner(const ThugCollisionInstance *);
void thug_moving_collision_update_bounds(ThugMovingCollisionInstance *);
const ThugBounds *thug_moving_collision_bounds(ThugCollisionInstance *);
uint8_t thug_moving_collision_intersects(const ThugCollisionInstance *, const ThugBounds *);
void thug_moving_collision_local_segment(const ThugMovingCollisionInstance *, const float input[8], float output[8]);
uint8_t thug_moving_collision_segment(const ThugCollisionInstance *, const float segment[8], const float delta[4],
    ThugCollisionResult *, const ThugBounds *, ThugCollisionQuery *);

typedef struct ThugMovingCollisionNode {
    uint32_t unknown_0;
    ThugCollisionInstance *object;
    uint32_t unknown_8;
    struct ThugMovingCollisionNode *next;
} ThugMovingCollisionNode;
extern ThugMovingCollisionNode *thug_moving_collision_list;
void *thug_moving_scene_segment(const float segment[8], ThugCollisionResult *,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *, ThugCollisionQuery *);
void *thug_moving_scene_segment_farthest(const float segment[8], ThugCollisionResult *,
    void (*callback)(ThugCollisionResult *), const ThugCollisionCache *, ThugCollisionQuery *);
#endif
