#ifndef THUG_SPHERE_QUERY_DRAFT_H
#define THUG_SPHERE_QUERY_DRAFT_H
#include "../../src/collision/scene.h"
typedef struct {
    float point[4], time, normal[4];
    uint32_t checksum;
    uint8_t flag_40, padding[3];
} ThugSphereHitDraft;
typedef struct {
    uint32_t unknown_0;
    ThugSphereHitDraft hits[32];
    float direction[4], travel;
    uint32_t count;
    uint16_t excluded_flags, required_flags;
    uint32_t mode;
} ThugSphereResultDraft;
typedef uint8_t (*ThugSphereMethodDraft)(const ThugCollisionInstance *, const float *,
    const ThugBounds *, ThugSphereResultDraft *, ThugCollisionQuery *);
uint8_t thug_static_collision_sphere_draft(const ThugCollisionInstance *, const float *,
    const ThugBounds *, ThugSphereResultDraft *, ThugCollisionQuery *);
#endif
