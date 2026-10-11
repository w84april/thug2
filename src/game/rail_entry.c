/* 0050a770: point kicks, Natas entry, lip entry and ordinary grind entry. */
#include "rail.h"
#include "grind.h"
#include "nodes.h"
#include "moving_contact.h"
#include "collision_events.h"
#include "stats.h"
#include "../audio/events.h"
#include "../script/delivery.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../core/number.h"
#include "../core/random.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
static uint32_t word(const void *p) {uint32_t v;__builtin_memcpy(&v,p,4);return v;}
static void store(void *p,uint32_t v) {__builtin_memcpy(p,&v,4);}
static void *pointer(const void *p) {return (void *)(uintptr_t)word(p);}
static float number(const void *p) {float v;__builtin_memcpy(&v,p,4);return v;}
static void copy4(float *to,const float *from) {
    for(unsigned i=0;i<4;++i)__builtin_memcpy(to+i,from+i,4);
}
static float negative(float f) {
    uint32_t w=word(&f)^0x80000000;
    if((w&0x7f800000)==0x7f800000&&(w&0x7fffff))w|=0x400000;
    __builtin_memcpy(&f,&w,4);return f;
}
static double dot_zyx(const float *a,const float *b) {
    return R(R(R((double)a[2]*b[2])+R((double)a[1]*b[1]))+R((double)a[0]*b[0]));
}
static void clear_flag(ThugSkaterState *state,unsigned offset) {
    uint8_t *f=(uint8_t *)state+offset;
    if(*f) {*f=0;store(f+4,thug_elapsed_time()+thug_timer_offset);}
}
static void clear_point_flags(ThugSkaterPhysics *p) {
    clear_flag(p->state,0x78);clear_flag(p->state,0xa8);
    clear_flag(p->state,0x80);clear_flag(p->state,0xb0);
}
static void upward(ThugSkaterPhysics *p,ThugCollisionQuery *q) {
    thug_skater_set_up_vector(p,0,1,0,1,q);
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
}
static void direct_material(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    uint8_t material=(uint8_t)p->rail_node->unknown_50;
    thug_skater_state_set_material(p->state,material,d,m);
    p->sound->unknown_1c[0]=material;
}
static void land_sound(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugSkaterBody *body=p->body;uint32_t material=p->state->material;
    float speed=(float)thug_vector_length(body->velocity);
    double maximum=thug_skater_stat_parameter(body,0xcc5f87aa);
    thug_sound_component_land(p->sound,(float)R((double)speed/maximum),material,d,m);
}
static const ThugReferencedObject *contact_owner(ThugSkaterPhysics *p,const ThugMemory *m) {
    ThugSkaterGroundGate *gate=p->ground_gate;
    if(!gate->contact)return 0;
    if(!gate->contact->reference.object) {thug_skater_moving_contact_release(gate,m);return 0;}
    return gate->contact->reference.object;
}
static void point_event(ThugSkaterPhysics *p,const uint32_t events[3],const ThugDiagnostics *d,const ThugMemory *m) {
    const ThugReferencedObject *owner=contact_owner(p,m);
    thug_collision_event_start(p->collision_events,events,p->rail_name,0,owner,d,m);
}
/* Three paths share the segment query, but Natas spills the differences and
 * sums X/Y/Z; the other two retain differences wide and sum Z/Y/X. */
static int blocked(ThugSkaterPhysics *p,const float *position,int natas,ThugCollisionQuery *q) {
    copy4(p->surface_segment,p->body->position);copy4(p->surface_segment+4,position);
    if(!thug_skater_query_surface(p,0x10,0,q))return 0;
    const float *hit=(const float *)((const uint8_t *)p+0x120);
    if(natas) {float delta[4];thug_vector_difference(delta,position,hit);return thug_vector_length_squared(delta)>36;}
    double x=R((double)position[0]-hit[0]),y=R((double)position[1]-hit[1]),z=R((double)position[2]-hit[2]);
    return R(R(R(z*z)+R(y*y))+R(x*x))>36;
}
static void project_horizontal(ThugSkaterPhysics *p,uint32_t walking) {
    if((uint8_t)walking)return;
    float *v=p->body->velocity;
    if(R(R((double)v[2]*v[2])+R((double)v[0]*v[0]))>100) {
        const float up[4]={0,1,0,1};thug_vector_project_preserve_length(v,up);
    }
}
static double angle(uint32_t name,uint32_t required) {
    return thug_platform_multiply_x87_single(thug_script_get_global_number(name,required),0.01745329238474369f);
}
static void boost(float *velocity,const float direction[4],double amount) {
    double x=R((double)direction[0]*amount);
    float y=(float)R((double)direction[1]*amount),z=(float)R((double)direction[2]*amount),w=(float)R((double)direction[3]*amount);
    velocity[0]=(float)R(x+velocity[0]);velocity[1]=(float)R((double)y+velocity[1]);
    velocity[2]=(float)R((double)z+velocity[2]);velocity[3]=(float)R((double)w+velocity[3]);
}
void thug_skater_enter_rail(ThugSkaterPhysics *p,const float position[4],ThugRailNode *node,ThugObjectTransform *transform,
    uint32_t suppress_lip,uint32_t walking,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugSkaterInput *input=p->input;ThugSkaterBody *parameter_body=p->body;uint8_t *raw=(void *)p;
    thug_skater_apply_pending_flip((void *)thug_object_find_component(p->body,0x488af07a),d,m);
    if(p->rail_node!=node) {
        uint32_t index=((uint32_t)(uintptr_t)node-(uint32_t)(uintptr_t)transform->rail_nodes)/0x54;
        thug_score_record_rail(p->score_component->score,(int32_t)index);
    }
    p->rail_transform=transform;p->rail_node=node;
    const uint32_t grind_events[3]={13,3,0},point_exit[3]={1,4,0},natas_events[3]={12,3,0},lip_events[3]={7,3,0};
    if(!node->previous&&!node->next) {
        int natas=0;
        if(input->button_100.pressed||input->button_a0.pressed) {
            uint32_t last=word(raw+0x1504);
            float elapsed=(float)(int32_t)(thug_elapsed_time()+thug_timer_offset-last);
            natas=!(R(thug_script_get_global_number(0x0a477668,1)*1000)>elapsed);
        }
        if(natas) {
            p->airborne_flag_2ec=1;raw[0x1500]=input->button_100.pressed!=0;
            if(blocked(p,position,1,q))return;
            copy4(p->body->position,position);clear_flag(p->state,0x30);clear_flag(p->state,0x38);
            p->ground_transition_flag=0;upward(p,q);thug_skater_change_state(p,4,d,m);
            thug_skater_set_material(p,(uint8_t)p->rail_node->unknown_50,d,m);
            if(!p->parameter_mode_active)land_sound(p,d,m);
            p->body->velocity[0]=0;p->body->velocity[1]=0;p->body->velocity[2]=0;
            p->rail_reentry_time=thug_elapsed_time()+thug_timer_offset;clear_point_flags(p);
            thug_object_emit_event((void *)p->body,0xda82d6d6,0,d,m);
            thug_skater_rail_event(p,natas_events,d,m);
            store(raw+0x1504,thug_elapsed_time()+thug_timer_offset);return;
        }
        if(blocked(p,position,0,q))return;
        ThugSkaterBody *body=p->body;
        if(__builtin_fabsf(body->velocity[0])<.009999999776482582f&&__builtin_fabsf(body->velocity[2])<.009999999776482582f) {
            body->velocity[0]=body->orientation[8];p->body->velocity[2]=p->body->orientation[10];
        }
        project_horizontal(p,walking);
        float direction[4];copy4(direction,p->body->velocity);direction[1]=0;thug_vector_normalize(direction);
        double radians=angle(0xbb357ecb,0),cosine=thug_platform_cos(radians);
        float kick[4]={(float)R((double)direction[0]*cosine),(float)thug_platform_sin(radians),(float)R((double)direction[2]*cosine),1};
        ThugScriptStructure *metadata=thug_node_find(p->rail_node->name,1);
        thug_script_get_checksum(metadata,0xa1dc81f9,&p->rail_name,1);
        thug_skater_notify(p->name_context,p->rail_name,d,m);
        uint32_t script=0;
        if(thug_script_get_checksum(metadata,0x2ca8a299,&script,0))point_event(p,grind_events,d,m);
        copy4(p->body->position,position);clear_flag(p->state,0x30);clear_flag(p->state,0x38);
        p->ground_transition_flag=0;if(p->state->mode==2)upward(p,q);
        thug_skater_change_state(p,4,d,m);direct_material(p,d,m);
        if(!p->parameter_mode_active)land_sound(p,d,m);
        uint32_t vertical=word(p->body->velocity+1);thug_vector_project_axis(p->body->velocity,direction);
        body=p->body;
        if((uint8_t)walking&&dot_zyx(body->velocity,body->orientation+8)<0) {
            float minimum=(float)R(thug_walk_parameter((uintptr_t)body->velocity,0x896c8888)*1.100000023841858f);
            if(R((double)minimum*minimum)>thug_vector_length_squared(body->velocity)) {
                body=p->body;body->velocity[0]=body->velocity[1]=body->velocity[2]=0;body->velocity[3]=1;
                copy4(direction,p->body->orientation+8);direction[1]=0;thug_vector_normalize(direction);
            }
        }
        store(p->body->velocity+1,vertical);
        double amount=thug_script_get_global_number(0xa3ef4833,1);boost(p->body->velocity,direction,amount);
        p->rail_reentry_time=thug_elapsed_time()+thug_timer_offset;clear_point_flags(p);
        p->rail_retry_delay=thug_truncate_double_low_word(thug_script_get_global_number(0x2b4645ad,1));
        clear_flag(p->state,0x50);thug_vector_align_magnitude(p->body->velocity,kick);
        if(script)point_event(p,point_exit,d,m);
        thug_skater_change_state(p,1,d,m);
        p->body->position[1]=(float)R((double)p->body->position[1]+1);
        thug_object_emit_event((void *)p->body,0xb8048f1d,0,d,m);return;
    }
    float lip_allow=(float)thug_platform_sin(angle(0x8157c5d9,1));
    if(node->flags&1)lip_allow=(float)thug_platform_sin(angle(0xf3b6f95e,1));
    float horizontal=(float)thug_platform_sin(angle(0xe2a85fbb,1));
    float vert=(float)thug_platform_cos(angle(0x61079462,1));
    ThugSkaterBody *body=p->body;
    if((raw[0x375]||(body->velocity[1]>0&&__builtin_fabsf(body->orientation[5])<horizontal&&body->orientation[9]>0&&
        __builtin_fabsf(p->orientation_target[1])<vert&&__builtin_fabsf(body->orientation[1])<lip_allow))&&!(uint8_t)suppress_lip&&!p->parameter_mode_active) {
        body->velocity[0]=body->velocity[1]=body->velocity[2]=0;body->velocity[3]=1;
        clear_flag(p->state,0x30);clear_flag(p->state,0x38);clear_flag(p->state,0x40);clear_flag(p->state,0x48);
        p->ground_transition_flag=0;thug_balance_context_stop((void *)p->mode_context,d,m);
        copy4(p->state_saved_position,p->body->position);thug_skater_change_state(p,3,d,m);copy4(p->body->position,position);
        float tangent[4];copy4(tangent,p->orientation_target);tangent[1]=0;thug_vector_normalize(tangent);
        float *matrix=p->body->orientation;matrix[5]=tangent[1];matrix[4]=tangent[0];matrix[7]=tangent[3];matrix[6]=tangent[2];
        matrix=p->body->orientation;matrix[8]=0;matrix[9]=1;matrix[10]=0;matrix[11]=1;
        matrix=p->body->orientation;float x=matrix[4],z=negative(matrix[6]);matrix[1]=0;matrix[3]=0;matrix[0]=z;matrix[2]=x;
        thug_matrix_copy(p->cached_orientation,p->body->orientation);
        thug_tricks_cancel((void *)thug_object_find_component(p->body,0x11b4c67f),0,0x100000,m);
        thug_skater_rail_event(p,lip_events,d,m);((uint8_t *)p->name_context)[0xa24]=0;
        if(!pointer((uint8_t *)p->body+0x10)) {
            ThugScriptInstance *instance=thug_script_allocate(sizeof(*instance),m);
            if(instance)thug_script_initialize(instance);
            store((uint8_t *)p->body+0x10,(uintptr_t)instance);
        }
        body=p->body;thug_script_setup_named(pointer((uint8_t *)body+0x10),0x1647cf96,0,(void *)body,d,m);
        thug_script_execute(pointer((uint8_t *)p->body+0x10),d,m);p->state->unknown_e0=1;direct_material(p,d,m);return;
    }
    direct_material(p,d,m);
    ThugRailNode *start=p->rail_node,*next=start->next;
    float a[4],b[4],direction[4];thug_rail_point(p->rail_transform,a,start);thug_rail_point(p->rail_transform,b,next);
    for(unsigned i=0;i<4;++i)direction[i]=(float)R((double)b[i]-a[i]);thug_vector_normalize(direction);
    if(blocked(p,position,0,q))return;
    if(p->state->transfer_flag_a8) {
        if(d&&d->print) {
            d->print(d->context,"M:%s:%i: %s\n","mponents\\SkaterCorePhysicsComponent.cpp",0x239c,"GRINDING FROM ACID DROP");
            d->print(d->context,"D:%s:%i: acid_hold = %g, %g, %g\n","mponents\\SkaterCorePhysicsComponent.cpp",0x239d,
                (double)thug_skater_transfer_velocity[0],(double)thug_skater_transfer_velocity[1],(double)thug_skater_transfer_velocity[2]);
        }
        float *v=p->body->velocity;
        for(unsigned i=0;i<4;++i)v[i]=(float)R((double)thug_skater_transfer_velocity[i]+v[i]);
    }
    body=p->body;
    if(body->velocity[0]==0&&body->velocity[2]==0) {body->velocity[0]=body->orientation[8];p->body->velocity[2]=p->body->orientation[10];}
    project_horizontal(p,walking);
    double along=dot_zyx(direction,p->body->velocity);
    float sign=along==0?(thug_random_range(2)?1:-1):(along<0?-1:1);
    ThugRailNode *end=sign<0?start:next;
    if(!(sign<0?start->previous:next->next)) {
        float endpoint[4];thug_rail_point(p->rail_transform,endpoint,end);
        if(thug_vector_equal(endpoint,position))return;
    }
    thug_skater_rail_event(p,grind_events,d,m);copy4(p->body->position,position);
    clear_flag(p->state,0x30);clear_flag(p->state,0x38);p->ground_transition_flag=0;
    if(p->state->mode==2)upward(p,q);thug_skater_change_state(p,4,d,m);
    uint32_t last=word((uint8_t *)p->wall_gate+0x1c);
    if(thug_elapsed_time()+thug_timer_offset-last&&!p->parameter_mode_active)land_sound(p,d,m);
    uint32_t vertical=word(p->body->velocity+1);thug_vector_project_axis(p->body->velocity,direction);body=p->body;
    if((uint8_t)walking&&dot_zyx(body->velocity,body->orientation+8)<0) {
        double minimum=R(thug_walk_parameter((uintptr_t)body->velocity,0x896c8888)*1.100000023841858f);
        const float *v=body->velocity;
        double squared=R(R(R((double)v[2]*v[2])+R((double)v[0]*v[0]))+R((double)v[1]*v[1]));
        if(R(minimum*minimum)>squared) {
            body=p->body;body->velocity[0]=body->velocity[1]=body->velocity[2]=0;body->velocity[3]=1;
            sign=(float)thug_sign_nonnegative((float)dot_zyx(direction,p->body->orientation+8));
        }
    }
    store(p->body->velocity+1,vertical);
    float travel[4];for(unsigned i=0;i<4;++i)travel[i]=(float)R((double)sign*direction[i]);
    double amount=thug_script_get_global_number(0x457bb395,1);boost(p->body->velocity,travel,amount);raw[0x34c]=0;
    if(sign<0)for(unsigned i=0;i<4;++i)direction[i]=negative(direction[i]);
    double side=R(R(-R((double)position[0]-number(raw+0x338))*direction[2])+R(R((double)position[2]-number(raw+0x340))*direction[0]));
    uint32_t approach=side<0,parallel=0;
    p->surface_segment[1]=(float)thug_skater_get_parameter(0xe4d79235,1,parameter_body);
    p->surface_segment[0]=p->surface_segment[2]=p->surface_segment[3]=0;
    p->surface_segment[5]=(float)-thug_script_get_global_number(0x9cd7ed5c,1);
    p->surface_segment[4]=p->surface_segment[6]=p->surface_segment[7]=0;
    for(unsigned i=0;i<4;++i)p->surface_segment[i]=(float)R((double)position[i]+p->surface_segment[i]);
    for(unsigned i=0;i<4;++i)p->surface_segment[i+4]=(float)R((double)position[i]+p->surface_segment[i+4]);
    double distance=thug_script_get_global_number(0x31669752,1);
    float offset[4]={(float)R((double)direction[2]*distance),(float)R(0.0*distance),(float)R((double)negative(direction[0])*distance),(float)R(0.0*distance)};
    for(unsigned i=0;i<8;++i)p->surface_segment[i]=(float)R((double)offset[i%4]+p->surface_segment[i]);
    uint8_t first=thug_skater_query_surface(p,0x10,0,q);
    double twice[4];for(unsigned i=0;i<4;++i)twice[i]=R((double)offset[i]+offset[i]);
    for(unsigned i=0;i<8;++i) {
        double delta=twice[i%4];if(i%4==0||i%4==3||i==6)delta=(float)delta;
        p->surface_segment[i]=(float)R((double)p->surface_segment[i]-delta);
    }
    uint8_t second=thug_skater_query_surface(p,0x10,0,q);
    raw[0x249]=(first&&!approach)||(second&&approach);raw[0x248]=first||second;
    body=p->body;float side_dot=(float)dot_zyx(direction,body->orientation),forward_dot=(float)dot_zyx(direction,body->orientation+8);
    double tolerance=thug_script_get_global_number(0xd0688d4e,1);
    float selected=side_dot;
    if(tolerance>__builtin_fabsf(side_dot)) {parallel=1;selected=forward_dot;}
    else if(p->state->stat_modifier_selector)selected=negative(selected);
    if(selected<0)raw[0x34c]=1;
    ((uint8_t *)p->name_context)[0xa24]=0;
    if(!thug_skater_run_pending_trick(p->name_context,approach,parallel,raw[0x34c],p->state->stat_modifier_selector,d,m)) {
        uint32_t stance=p->state->stat_modifier_selector,reverse=raw[0x34c];
        uint32_t variant=thug_grind_trick_variant(input->button_20.pressed,input->button_40.pressed,input->button_60.pressed,input->button_80.pressed);
        thug_skater_start_grind_script(p,variant,approach,parallel,reverse,stance,d,m);
    }
    p->rail_reentry_time=thug_elapsed_time()+thug_timer_offset;
}
