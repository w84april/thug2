#ifndef THUG_OBJECT_FRAME_H
#define THUG_OBJECT_FRAME_H
#include "skater.h"
/* Recovered virtual update/notification slots receive host context explicitly. */
typedef void (*ThugObjectFrameStep)(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_object_update_components(ThugSkaterBody *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_object_mark_moved(ThugSkaterBody *,uint32_t,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_component_physics_frame_bridge(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void thug_component_empty_frame_bridge(void *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
#endif
