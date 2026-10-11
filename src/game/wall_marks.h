#ifndef THUG_GAME_WALL_MARKS_H
#define THUG_GAME_WALL_MARKS_H
#include "../graphics/decal_scene.h"
#include "../platform/diagnostics.h"
typedef struct {
    uint8_t unknown_0_to_b[12];
    void *owner;
    uint8_t unknown_10_to_1b[12];
    void *plain_texture,*rotated_texture;
} ThugWallMarkEmitter;
extern const char thug_wall_mark_empty_texture[];
/* The PC receives both vectors by value. The port captures these words before
 * any game or host callback, preserving that original argument lifetime. */
void thug_wall_mark_emit(ThugWallMarkEmitter *,uint32_t kind,const float from[4],
    const float to[4],int32_t size,uint32_t send,const ThugDiagnostics *,const ThugMemory *);
typedef struct ThugWallContactMark {
    uint8_t unknown_0_to_b[12];
    void *owner;
    uint8_t unknown_10_to_17[8];
    int32_t inhibit;
    uint8_t armed,unknown_1d_to_1f[3];
    float cooldown;
    void *direction;
    uint32_t unknown_28;
    void *body_component;
    uint32_t unknown_30;
    ThugWallMarkEmitter *emitter;
} ThugWallContactMark;
extern const char thug_wall_contact_missing[],thug_wall_contact_emitting[];
/* Requires the configured distance member and valid engine collision state. */
uint8_t thug_wall_contact_mark(ThugWallContactMark *,uint32_t kind,uint32_t use_direction,
    uint32_t lower_origin,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
#endif
