#ifndef THUG_COLLISION_GEOMETRY_H
#define THUG_COLLISION_GEOMETRY_H
#include "tree.h"

float *thug_collision_vertex(const ThugCollisionObject *object, float output[4], uint32_t index);
void thug_collision_vertex_into(const ThugCollisionObject *object, uint32_t index, float output[4]);
float *thug_collision_face_normal(const ThugCollisionObject *object, float output[4], uint32_t face);
uint8_t thug_collision_triangle(const float origin[4], const float delta[4],
    const float a[4], const float b[4], const float c[4], float *fraction);
#endif
