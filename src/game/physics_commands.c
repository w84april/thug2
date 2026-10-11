#include "components.h"
#include "../script/delivery.h"
#include "animation.h"
#include "../script/execute.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static uint32_t word(const void *p,unsigned off){uint32_t v;__builtin_memcpy(&v,(const uint8_t *)p+off,4);return v;}
static void store(void *p,unsigned off,uint32_t v){__builtin_memcpy((uint8_t *)p+off,&v,4);}
typedef uint32_t (*Command)(void *,uint32_t,ThugScriptStructure *,ThugScriptInstance *);

/* The original command slot keeps its four-argument ABI. Host services are
 * scoped around entry, with restoration for nested command calls. These
 * adapters are platform plumbing, not additional recovered game routines. */
uint32_t thug_motion_command(ThugObjectComponent *,uint32_t,const ThugScriptStructure *,ThugScriptInstance *,const ThugDiagnostics *,const ThugMemory *);
uint32_t thug_motion_command_bridge(void *p,uint32_t name,ThugScriptStructure *parameters,ThugScriptInstance *script){
    const ThugEventServices *event=thug_event_services;
    return thug_motion_command(p,name,parameters,script,event?event->diagnostics:thug_component_services->diagnostics,event?event->memory:thug_component_services->memory);
}
/* 00501600. Ledge query and Obj_MoveToNode are the only recognized commands.
 * The Motion virtual call precedes physics, shadow and camera synchronization.
 * Reset may deliver QB events; reload owner/state pointers after callbacks. */
static uint32_t command(ThugSkaterPhysics *p,uint32_t name,ThugScriptStructure *parameters,ThugScriptInstance *script,const ThugComponentServices *s){
    if(name==0x315d9ed4)return ((const uint8_t *)p)[0x248]!=0;
    if(name!=0x8819dd8b)return 2;
    ThugObjectComponent *motion=thug_object_find_component(p->body,0x0a015e17);
    Command dispatch;__builtin_memcpy(&dispatch,(const uint8_t *)(uintptr_t)motion->unknown_0+0x30,4);
    uint8_t result=dispatch(motion,name,parameters,script)!=0;
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
    void *shadow=thug_object_find_component(p->body,0x8a897dd2);
    thug_shadow_set_position(shadow,p->body->position);
    thug_shadow_set_up(shadow,p->body->orientation+4);
    thug_vector_copy(p->side_previous_position,p->body->position);
    ThugSkaterBody *body=p->body;
    thug_vector_copy(body->previous_position,body->position);
    thug_object_mark_moved(p->body,1,s->query,s->diagnostics,s->memory);
    body=p->body;
    if(body->parameter_sets_enabled){
        ThugSkaterBody *camera=thug_skater_camera_object(body);
        if(camera)thug_object_update_components(camera,s->query,s->diagnostics,s->memory);
    }
    if(!thug_script_has_flag(parameters,0xd607e2e6)){
        body=p->body;((uint8_t *)p)[0x1c5]=0;
        store(body,0xac,0);store(body,0xb0,0);store(body,0xb4,0);store(body,0xb8,0x3f800000);
        thug_skater_change_state(p,0,s->diagnostics,s->memory);
        body=p->body;ThugSkaterState *state=p->state;
        uint8_t flipped=body->stat_modifier_selector==0;
        if(state->stat_modifier_selector!=flipped){
            state->stat_modifier_selector=flipped;
            state->stat_modifier_time=thug_elapsed_time()+thug_timer_offset;
        }
        thug_skater_sync_flip((void *)thug_object_find_component(p->body,0x488af07a),s->diagnostics,s->memory);
        return result;
    }
    if(thug_script_has_flag(parameters,0x90a91232)){
        body=p->body;uint32_t vertical=word(body,0xb0);store(body,0xb0,0);
        body=p->body;
        double x=body->velocity[0],y=body->velocity[1],z=body->velocity[2];
        double sum=R(R(x*x)+R(y*y));sum=R(sum+R(z*z));
        float magnitude=(float)R(__builtin_sqrt(sum)),v[4];
        thug_vector_scaled_copy(v,body->orientation+8,magnitude);
        thug_vector_copy(body->velocity,v);store(p->body,0xb0,vertical);
    }
    return result;
}
uint32_t thug_skater_physics_command(ThugSkaterPhysics *p,uint32_t name,ThugScriptStructure *parameters,ThugScriptInstance *script,ThugCollisionQuery *query,const ThugDiagnostics *d,const ThugMemory *m){
    const ThugComponentServices s={query,d,m},*previous=thug_component_services;thug_component_services=&s;
    uint32_t result=command(p,name,parameters,script,&s);thug_component_services=previous;return result;
}
#undef R
