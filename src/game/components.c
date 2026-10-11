#include "components.h"
#include "drawing.h"
#include "animation_controllers.h"
#include "../core/line.h"
#include "../script/execute.h"
#include "../script/delivery.h"
#include <stddef.h>
_Static_assert(sizeof(ThugComponentMethods)==52,"Thirteen original component slots");
_Static_assert(offsetof(ThugComponentMethods,descriptor)==0x2c,"Descriptor slot");
_Static_assert(offsetof(ThugComponentMethods,checksum)==0x30,"Checksum slot");
extern const ThugComponentMethods thug_component_methods,thug_physics_methods;
static const ThugComponentMethods *methods(void *component){return (const void *)(uintptr_t)((ThugObjectComponent *)component)->unknown_0;}
static void set_methods(void *component,const ThugComponentMethods *table){((ThugObjectComponent *)component)->unknown_0=(uintptr_t)table;}
/* 0045d730. Owner, type and next are deliberately untouched. */
void *thug_component_construct(void *component){
    set_methods(component,&thug_component_methods);((ThugObjectComponent *)component)->unknown_8=0;return component;
}
/* 0045d740. Destruction invalidates component waits only when bit one is set. */
void thug_component_destroy(void *component){
    uint32_t flags=((ThugObjectComponent *)component)->unknown_8;
    set_methods(component,&thug_component_methods);
    if(flags&2)thug_script_clear_component_waits(component);
}
/* 0045d780. Return the original pointer even after conditional heap release. */
void *thug_component_delete(void *component,uint32_t flags,const ThugMemory *m){
    thug_component_destroy(component);if((uint8_t)flags&1)m->release(m->context,component);return component;
}
/* 0045d760. */
void thug_component_suspend(void *component,uint32_t enabled){
    ThugObjectComponent *p=component;
    p->unknown_8=(uint8_t)enabled?p->unknown_8|1:p->unknown_8&~1u;
}
/* 004e3f90, 0048dcd0 and005bab90. The latter two really are bare RET8/RET4. */
void thug_component_refresh(void *component,const ThugScriptStructure *parameters){methods(component)->initialize(component,parameters);}
void thug_component_empty_two(void *component,void *a,void *b){(void)component;(void)a;(void)b;}
void thug_component_empty_one(void *component,void *a){(void)component;(void)a;}
/* 0045d720. Base descriptor forwarding ignores extended descriptor fields. */
uint32_t thug_component_descriptor_base(void *component,const ThugScriptCommand *descriptor,ThugScriptStructure *parameters,ThugScriptInstance *script){
    return methods(component)->checksum(component,descriptor->name,parameters,script);
}
/* 0042bb20. Extended descriptors optionally contain a direct member entry and
 * a byte adjustment to its receiver, otherwise use virtual checksum dispatch. */
uint32_t thug_component_descriptor(void *component,const ThugScriptCommand *descriptor,ThugScriptStructure *parameters,ThugScriptInstance *script){
    typedef uint32_t (*Member)(void *,ThugScriptStructure *,ThugScriptInstance *);
    Member member;uint32_t adjustment;
    __builtin_memcpy(&member,(const uint8_t *)descriptor+8,4);
    if(member){
        __builtin_memcpy(&adjustment,(const uint8_t *)descriptor+12,4);
        return member((void *)((uintptr_t)component+adjustment),parameters,script);
    }
    return methods(component)->checksum(component,descriptor->name,parameters,script);
}
/* 00500ca0. Constructor order and all untouched storage match the PC body.
 * Win32 SEH registration belongs to the host ABI, not the game data. */
void *thug_physics_construct(void *component){
    ThugSkaterPhysics *p=thug_component_construct(component);
    set_methods(p,&thug_physics_methods);
    thug_collision_probe_initialize(&p->surface_probe);
    thug_collision_probe_initialize(&p->saved_probe);
    p->attachment_reference.previous=p->attachment_reference.next=NULL;p->attachment_reference.object=NULL;
    thug_segment_initialize((uint8_t *)p+0x3f0);
    thug_collision_cache_initialize((void *)((uint8_t *)p+0x4f4));
    for(unsigned i=0x150c;i<=0x1538;i+=4)__builtin_memcpy((uint8_t *)p+i,&(uint32_t){0},4);
    p->special_timer_active=0;p->unknown_2d8=0;p->ground_flag_2e4=0;p->parameter_mode_active=0;p->reverse_script_requested=0;
    ((ThugObjectComponent *)p)->type=0x5bd63b29;
    p->projectile_input_value=UINT32_MAX;p->rotation_step=1;return p;
}
/* 004fc500 /00500db0. Unregister the cache, unlink all three live references,
 * then change to the base table and clear waits before optional heap release. */
void thug_physics_destroy(void *component){
    ThugSkaterPhysics *p=component;set_methods(p,&thug_physics_methods);
    thug_collision_cache_destroy((void *)((uint8_t *)p+0x4f4));
    thug_object_reference_destroy(&p->attachment_reference);
    thug_object_reference_destroy(&p->saved_probe.moving_object);
    thug_object_reference_destroy(&p->surface_probe.moving_object);
    thug_component_destroy(p);
}
void *thug_physics_delete(void *component,uint32_t flags,const ThugMemory *m){
    thug_physics_destroy(component);if((uint8_t)flags&1)m->release(m->context,component);return component;
}
/* 00505440. The actual registry factory zero-allocates the full component
 * before construction. Successful allocation is the normal host contract;
 * retain the original null result on allocation failure. */
void *thug_physics_create(const ThugMemory *m){
    void *component=thug_allocate_zeroed(0x153c,m);
    return component?thug_physics_construct(component):NULL;
}
/* Fixed command ABI plus scoped host services. Entry points restore the prior
 * scope on return, so nested QB commands retain their caller's collision query.
 * The existing interpreter supplies current diagnostics/memory in event scope.
 * These bridges and the runtime purecall traps are not recovered game routines. */
const ThugComponentServices *thug_component_services;
uint32_t thug_skater_physics_command(ThugSkaterPhysics *,uint32_t,ThugScriptStructure *,ThugScriptInstance *,ThugCollisionQuery *,const ThugDiagnostics *,const ThugMemory *);
static uint32_t physics_checksum(void *component,uint32_t name,ThugScriptStructure *parameters,ThugScriptInstance *script){
    const ThugEventServices *event=thug_event_services;
    return thug_skater_physics_command(component,name,parameters,script,thug_component_services->query,
        event?event->diagnostics:thug_component_services->diagnostics,event?event->memory:thug_component_services->memory);
}
uint32_t thug_component_descriptor_scoped(void *component,const ThugScriptCommand *descriptor,ThugScriptStructure *parameters,ThugScriptInstance *script,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
    uint32_t value=thug_component_descriptor(component,descriptor,parameters,script);thug_component_services=previous;return value;
}
static void physics_initialize(void *component,const ThugScriptStructure *parameters){thug_skater_initialize_physics(component,parameters);}
static void physics_finalize(void *component){thug_skater_link_physics(component);}
static void empty(void *component){thug_draw_style_noop(component);}
static uint32_t unhandled(void *component,uint32_t name,ThugScriptStructure *parameters,ThugScriptInstance *script){
    return thug_animation_unhandled_command(component,name,parameters,script,NULL,NULL);
}
/* MSVC purecall623771 is a runtime failure, not an empty abstract method. */
static void abstract_initialize(void *component,const ThugScriptStructure *parameters){(void)component;(void)parameters;__builtin_trap();}
static void abstract_frame(void *component,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){(void)component;(void)q;(void)d;(void)m;__builtin_trap();}
/* Exact slot order from647618 and64bc48, with typed host-context bridges. */
const ThugComponentMethods thug_component_methods={
    thug_component_delete,abstract_frame,abstract_initialize,empty,empty,
    thug_component_refresh,thug_component_empty_two,thug_component_suspend,
    thug_component_empty_one,thug_component_empty_frame_bridge,thug_component_empty_one,
    thug_component_descriptor_base,unhandled
};
const ThugComponentMethods thug_physics_methods={
    thug_physics_delete,thug_component_physics_frame_bridge,physics_initialize,physics_finalize,empty,
    thug_component_refresh,thug_component_empty_two,thug_component_suspend,
    thug_component_empty_one,thug_component_empty_frame_bridge,thug_component_empty_one,
    thug_component_descriptor,physics_checksum
};

/* Host entry for startup QB outside an object frame; not a new recovered routine. */
uint32_t thug_component_execute_script(ThugScriptInstance *script,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugComponentServices services={q,d,m},*previous=thug_component_services;thug_component_services=&services;
    uint32_t value=thug_script_execute(script,d,m);thug_component_services=previous;return value;
}
