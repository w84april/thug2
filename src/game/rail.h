#ifndef THUG_GAME_RAIL_H
#define THUG_GAME_RAIL_H
#include "skater.h"
typedef struct ThugRailNode {
    float minimum[4], maximum[4];
    float position[4];
    uint8_t unknown_30_to_3f[16];
    struct ThugRailNode *next, *previous;
    uint32_t flags, name, unknown_50;
} ThugRailNode;
float *thug_rail_point(const ThugObjectTransform *,float out[4],const ThugRailNode *);
uint8_t thug_skater_rail_eligible(ThugSkaterPhysics *,ThugRailNode *,uint32_t unused,uint32_t force);
void thug_skater_rail_event(ThugSkaterPhysics *,const uint32_t events[3],const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_rail_clearance(float ax,float ay,float az,float aw,float bx,float by,float bz,float bw,ThugCollisionQuery *);
int32_t thug_rail_side(const ThugRailNode *,const float direction[4],ThugCollisionQuery *);
uint8_t thug_rail_search(ThugObjectTransform *,const float from[4],const float to[4],float out[4],ThugRailNode **out_node,const ThugRailNode *skip,float minimum_alignment,int32_t requested_side,ThugCollisionQuery *);
void thug_skater_enter_rail(ThugSkaterPhysics *,const float position[4],ThugRailNode *,ThugObjectTransform *,uint32_t suppress_lip,uint32_t walking,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_acquire_rail(ThugSkaterPhysics *,uint32_t force,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_natas(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_transition_rail(ThugSkaterPhysics *,const float prior[4],ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_skater_update_rail(ThugSkaterPhysics *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
#endif
