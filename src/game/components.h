#ifndef THUG_GAME_COMPONENTS_H
#define THUG_GAME_COMPONENTS_H
#include "object_frame.h"
#include "../script/execute.h"
typedef uint32_t (*ThugComponentChecksum)(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);
typedef uint32_t (*ThugComponentDescriptor)(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
typedef struct {
    void *(*dispose)(void *,uint32_t,const ThugMemory *);
    ThugObjectFrameStep update;
    void (*initialize)(void *,const ThugScriptStructure *);
    void (*finalize)(void *);
    void (*unknown_10)(void *);
    void (*refresh)(void *,const ThugScriptStructure *);
    void (*unknown_18)(void *,void *,void *);
    void (*suspend)(void *,uint32_t);
    void (*unknown_20)(void *,void *);
    ThugObjectFrameStep moved;
    void (*unknown_28)(void *,void *);
    ThugComponentDescriptor descriptor;
    ThugComponentChecksum checksum;
} ThugComponentMethods;
extern const ThugComponentMethods thug_component_methods,thug_physics_methods;
/* Host context for the original fixed-argument virtual ABI. Scope it around
 * object updates, physics commands or explicit startup-script entry; nested
 * entries must restore the previous pointer. No collision fallback is supplied. */
typedef struct {ThugCollisionQuery *query;const ThugDiagnostics *diagnostics;const ThugMemory *memory;} ThugComponentServices;
extern const ThugComponentServices *thug_component_services;
uint32_t thug_component_execute_script(ThugScriptInstance *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void *thug_component_construct(void *);
void thug_component_destroy(void *);
void *thug_component_delete(void *,uint32_t,const ThugMemory *);
void thug_component_suspend(void *,uint32_t);
void thug_component_refresh(void *,const ThugScriptStructure *);
void thug_component_empty_one(void *,void *);
void thug_component_empty_two(void *,void *,void *);
uint32_t thug_component_descriptor_base(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
uint32_t thug_component_descriptor(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *);
uint32_t thug_component_descriptor_scoped(void *,const ThugScriptCommand *,ThugScriptStructure *,ThugScriptInstance *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
void *thug_physics_construct(void *);
void thug_physics_destroy(void *);
void *thug_physics_delete(void *,uint32_t,const ThugMemory *);
void *thug_physics_create(const ThugMemory *);
void thug_motion_orient_to_node(ThugObjectComponent *,const ThugScriptStructure *);
void thug_motion_arrive_at_node(ThugObjectComponent *,uint32_t,const ThugDiagnostics *,const ThugMemory *);
uint8_t thug_motion_move_to_position(ThugObjectComponent *,const ThugScriptStructure *,ThugScriptInstance *,float,float,float,float,uint32_t);
void thug_motion_move_to_node(ThugObjectComponent *,const ThugScriptStructure *,ThugScriptInstance *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_motion_command(ThugObjectComponent *,uint32_t,const ThugScriptStructure *,ThugScriptInstance *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_motion_command_bridge(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);
uint32_t thug_skater_physics_command(ThugSkaterPhysics *,uint32_t,ThugScriptStructure *,ThugScriptInstance *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
#endif
