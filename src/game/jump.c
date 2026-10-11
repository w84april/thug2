#include "jump.h"
#include "collision_events.h"
#include "rail.h"
#include "stats.h"
#include "../audio/jump.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../script/delivery.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
extern const uint32_t thug_vert_wallplant_events[3];
const uint32_t thug_jump_rail_events[3]={12,2,0}; /* 0064bc10 */
_Static_assert(offsetof(ThugSkaterPhysics,orientation_source)==0x58,"Jump impulse normal");
_Static_assert(offsetof(ThugSkaterPhysics,saved_probe)==0x158,"Jump source surface");
_Static_assert(offsetof(ThugSkaterPhysics,input_release_elapsed)==0x378,"Signed jump charge");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_gate_time)==0x4ec,"Jump timestamp");
static void jump_sound(ThugSkaterPhysics *p,uint32_t material,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugSkaterBody *body=p->body;
    double x=body->velocity[0],y=body->velocity[1],z=body->velocity[2];
    float speed=(float)R(__builtin_sqrt(R(R(R(x*x)+R(y*y))+R(z*z))));
    double scale=thug_skater_stat_parameter(body,0xcc5f87aa);
    float fraction=(float)R(speed/scale);
    thug_sound_component_jump(p->sound,fraction,material,d,m);
}
/* 00509450. Retain event order, live pointer reloads and asymmetric x87 spills.
 * The ground/air sound material occupies only the original stack byte; higher
 * undefined bytes do not affect the recovered material/packet callees. */
void thug_skater_jump(ThugSkaterPhysics *p,const ThugScriptStructure *params,
    ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    uint8_t audible=!thug_script_has_flag(params,0xe13620a8);
    uint32_t mode=p->state->mode;
    if(mode==0) {
        thug_collision_event_from_probe(p->collision_events,thug_vert_wallplant_events,&p->saved_probe,d,m);
        if(p->wall_gate->wall_response_suppressed)return;
        thug_vector_copy((float *)(void *)p->unknown_338_to_347,p->body->position);
        if(audible)jump_sound(p,((const uint8_t *)p)[0x1aa],d,m);
        thug_skater_prepare_floor_transition(p,q,d);
        ThugSkaterState *state=p->state;
        if(state->transition_flag_48!=1){state->transition_flag_48=1;state->transition_time_4c=thug_elapsed_time()+thug_timer_offset;}
    } else if(mode==1) {
        if(audible)jump_sound(p,((const uint8_t *)p)[0x1aa],d,m);
    } else if(mode==4&&audible)jump_sound(p,((const uint8_t *)p->state)[0xe1],d,m);
    int32_t limit=(int32_t)thug_script_get_global_integer(0xf733c097,1);
    int32_t elapsed=(int32_t)p->input_release_elapsed;
    if(elapsed>=limit)elapsed=limit;
    p->input_release_elapsed=(uint32_t)elapsed;
    ThugSkaterState *state=p->state;
    uint8_t vert=state->ground_transition_flag||(state->mode==0&&state->surface_flag_8);
    uint32_t high,low;
    if(thug_script_has_flag(params,0xec6b7fc7)){
        high=vert?0x39766891:0x8851a76e;low=vert?0x4cdb18cb:0x6e8efe38;
    }else{high=vert?0x9f79c8ea:0x02ade3ad;low=vert?0x91b07824:0xc8815e43;}
    float maximum=(float)thug_skater_stat_parameter(p->body,high);
    double minimum=thug_skater_stat_parameter(p->body,low);
    double fraction=R((double)(int32_t)p->input_release_elapsed/limit);
    float impulse=(float)R(R(R((double)maximum-minimum)*fraction)+minimum);
    thug_script_get_float(params,0xf0d90109,&impulse,0);
    state=p->state;
    if(state->drag_coefficient_selector){state->drag_coefficient_selector=0;state->drag_selector_time=thug_elapsed_time()+thug_timer_offset;}
    if(p->state->ground_transition_flag&&p->body->velocity[1]<0){
        ThugSkaterBody *body=p->body;double delta[4];
        for(unsigned i=0;i<4;i++){delta[i]=R((double)impulse*p->orientation_source[i]);if(i>=2)delta[i]=(float)delta[i];}
        for(unsigned i=0;i<4;i++)body->velocity[i]=(float)R(delta[i]+body->velocity[i]);
        state=p->state;impulse=0;
        if(state->ground_transition_flag){state->ground_transition_flag=0;state->ground_transition_time=thug_elapsed_time()+thug_timer_offset;}
        p->ground_transition_flag=0;
    }else if(p->body->velocity[1]<0)p->body->velocity[1]=0;
    ThugSkaterBody *body=p->body;
    body->velocity[1]=(float)R((double)impulse+body->velocity[1]);
    body=p->body;
    if(body->orientation[5]<-0.10000000149011612f){
        body->velocity[1]=(float)R((double)body->velocity[1]-R((double)impulse*1.5));
        body=p->body;double delta[4];
        for(unsigned i=0;i<4;i++){delta[i]=R((double)body->orientation[4+i]*12);if(i>=2)delta[i]=(float)delta[i];}
        for(unsigned i=0;i<4;i++)body->position[i]=(float)R(delta[i]+body->position[i]);
    }
    mode=p->state->mode;
    if(mode==4||(mode==1&&p->previous_state==4))thug_skater_jump_turn(p);
    if(p->airborne_flag_2ec)thug_skater_rail_event(p,thug_jump_rail_events,d,m);
    thug_skater_change_state(p,1,d,m);
    uint32_t now=thug_elapsed_time()+thug_timer_offset;
    body=p->body;p->transfer_gate_time=now;
    thug_object_broadcast_event((ThugReferencedObject *)body,0x8687163a,NULL,0,d,m);
}
/* 00509a40. The script argument is unused; return1 even after a blocked jump. */
uint32_t thug_skater_jump_command(ThugSkaterPhysics *p,const ThugScriptStructure *params,ThugScriptInstance *script,
    ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m){
    (void)script;thug_skater_jump(p,params,q,d,m);return 1;
}
/* Host bridge for the original fixed descriptor ABI; not another recovery. */
uint32_t thug_skater_jump_member(void *p,ThugScriptStructure *params,ThugScriptInstance *script){
    const ThugEventServices *e=thug_event_services;
    return thug_skater_jump_command(p,params,script,thug_component_services->query,
        e?e->diagnostics:thug_component_services->diagnostics,e?e->memory:thug_component_services->memory);
}
#undef R

#define R thug_platform_round_x87_single
/* 005002d0. Left has priority over right. Rotate horizontal velocity first,
 * then premultiply the owner and cached bases through the selected backend. */
void thug_skater_jump_turn(ThugSkaterPhysics *p) {
    float radians;
    if(p->input->button_60.pressed)
        radians=(float)thug_platform_multiply_x87_single(thug_script_get_global_number(0x38505ef3,1),0.01745329238474369f);
    else if(p->input->button_80.pressed)
        radians=(float)thug_platform_multiply_x87_single(thug_script_get_global_number(0x38505ef3,1),-0.01745329238474369f);
    else return;
    ThugSkaterBody *body=p->body;
    double sine=thug_platform_sin(radians),cosine=thug_platform_cos(radians);
    double x=body->velocity[0],z=body->velocity[2];
    body->velocity[0]=(float)R(R(cosine*x)+R(sine*z));
    body->velocity[2]=(float)R(R(cosine*z)+-R(x*sine));
    float rotation[16];float *target=p->body->orientation;
    thug_matrix_rotation_y(rotation,radians);thug_matrix_multiply(target,rotation,target);
    thug_matrix_rotation_y(rotation,radians);thug_matrix_multiply(p->cached_orientation,rotation,p->cached_orientation);
}
#undef R
