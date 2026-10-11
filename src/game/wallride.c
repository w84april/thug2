#include "skater.h"
#include "../core/vector.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
/* 005051b0. Raised wall-normal probe, then a projected correction
 * sweep and velocity projection against the first contact normal. */
uint8_t thug_skater_wall_overhang(ThugSkaterPhysics *p,ThugCollisionQuery *query) {
    ThugSkaterBody *body=p->body;
    double x=R((double)p->wall_transition_normal[0]*18);
    float scaled[4];
    for(unsigned i=1;i<4;++i)scaled[i]=(float)R((double)p->wall_transition_normal[i]*18);
    p->surface_segment[0]=(float)R(x+body->position[0]);
    for(unsigned i=1;i<4;++i)p->surface_segment[i]=(float)R((double)scaled[i]+body->position[i]);
    thug_vector_copy(p->surface_segment+4,p->surface_segment);
    p->surface_segment[5]=(float)R(thug_skater_get_parameter(0x542cf0c7,1,body)+p->surface_segment[5]);
    if(!thug_skater_query_surface(p,0x10,0,query))return 0;
    float normal[4];thug_vector_copy(normal,p->surface_probe.normal);
    if(normal[1]>-.10000000149011612f)return 0;
    float correction[4];thug_vector_difference(correction,p->surface_probe.point,p->surface_segment+4);
    thug_vector_project_axis(correction,normal);
    thug_vector_copy(p->surface_segment,p->body->position);
    for(unsigned i=0;i<4;++i)p->surface_segment[4+i]=(float)R((double)correction[i]+p->body->position[i]);
    if(thug_skater_query_surface(p,0x10,0,query)) {
        for(unsigned i=0;i<4;++i)p->body->position[i]=(float)R((double)p->surface_probe.normal[i]+p->surface_probe.point[i]);
    } else thug_vector_copy(p->body->position,p->surface_segment+4);
    thug_vector_project_plane(p->body->velocity,normal);
    return 1;
}

#undef R

/* 0050f830: complete wallride update. */
#include "skater.h"
#include "rail.h"
#include "moving_contact.h"
#include "collision_events.h"
#include "objectives.h"
#include "../audio/events.h"
#include "../script/delivery.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static void mark(ThugSkaterState *state,unsigned offset,uint8_t value) {
    uint8_t *flag=(uint8_t *)state+offset;
    if(*flag!=value) {*flag=value;uint32_t now=thug_elapsed_time()+thug_timer_offset;__builtin_memcpy(flag+4,&now,4);}
}
static float negative(float f) {
    uint32_t bits;__builtin_memcpy(&bits,&f,4);bits^=0x80000000;
    if((bits&0x7f800000)==0x7f800000&&(bits&0x7fffff))bits|=0x400000;
    __builtin_memcpy(&f,&bits,4);return f;
}
/* X, or X/Y, remains in x87 registers until the destination addition. */
static void add_scaled(float destination[4],const float direction[4],double amount,unsigned wide) {
    double delta[4];
    for(unsigned i=0;i<4;++i) {
        delta[i]=thug_platform_multiply_x87_single(amount,direction[i]);
        if(!(wide&(1u<<i)))delta[i]=(float)delta[i];
    }
    for(unsigned i=0;i<4;++i)destination[i]=(float)R(delta[i]+destination[i]);
}
static void normalize_zyx(float value[4]) {
    double length=R(__builtin_sqrt(thug_vector_dot(value,value)));
    if(length>0) {double scale=R(1/length);for(unsigned i=0;i<3;++i)value[i]=(float)R(scale*value[i]);}
}
static void cache_orientation(ThugSkaterPhysics *p) {thug_matrix_copy(p->cached_orientation,p->body->orientation);}
static void up(ThugSkaterPhysics *p,ThugCollisionQuery *q) {thug_skater_set_up_vector(p,0,1,0,1,q);}
static void leave_events(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    thug_skater_change_state(p,1,d,m);
    thug_object_broadcast_event((void *)p->body,0xd96f01f1,0,0,d,m);
    thug_object_emit_event((void *)p->body,0x3b1001b6,0,d,m);
}
static void move_away(ThugSkaterPhysics *p,ThugCollisionQuery *q,int cache,const ThugDiagnostics *d,const ThugMemory *m) {
    up(p,q);if(cache)cache_orientation(p);
    add_scaled(p->body->position,p->wall_transition_normal,18,3);leave_events(p,d,m);
}
static void collision_event(ThugSkaterPhysics *p,const uint32_t events[3],const ThugDiagnostics *d,const ThugMemory *m) {
    thug_collision_event_from_probe(p->collision_events,events,&p->saved_probe,d,m);
}
static int interrupted(const ThugSkaterPhysics *p) {return ((const uint8_t *)p->wall_gate)[0x26]!=0;}
static void segment_endpoint(ThugSkaterPhysics *p,float out[4],const float axis[4],double distance) {
    float scaled[4];for(unsigned i=0;i<4;++i)scaled[i]=(float)thug_platform_multiply_x87_single(distance,axis[i]);
    out[2]=scaled[2];out[3]=scaled[3];out[0]=scaled[0];out[1]=scaled[1];
    const float *position=p->body->position;
    out[0]=(float)R((double)out[0]+position[0]);
    for(unsigned i=1;i<4;++i)out[i]=(float)R((double)position[i]+out[i]);
}
void thug_skater_update_wallride(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    mark(p->state,0x78,0);mark(p->state,0xa8,0);mark(p->state,0x80,0);mark(p->state,0xb0,0);
    p->ground_flag_2e4=0;p->rail_node=0;p->ground_value_244=0;p->wall_transition_time=thug_elapsed_time()+thug_timer_offset;
    float displacement[4]={0,0,0,1};ThugSkaterGroundGate *gate=p->ground_gate;
    if(gate->contact) {
        if(!gate->contact->reference.object)thug_skater_moving_contact_release(gate,m);
        else if(!thug_moving_contact_update(gate->contact,p->body->position))thug_skater_moving_contact_release(gate,m);
        else {
            ThugMovingContact *contact=p->ground_gate->contact;thug_vector_copy(displacement,contact->displacement);
            if(contact->orientation_changed) {
                thug_matrix_multiply(p->body->orientation,p->body->orientation,contact->rotation);
                thug_matrix_multiply(p->cached_orientation,p->cached_orientation,p->ground_gate->contact->rotation);
            }
        }
    }
    ThugSkaterBody *parameter_body=p->body;
    float gravity=(float)thug_skater_get_parameter(0x0c617caf,1,parameter_body);
    double half=R(R((double)p->time_step*p->time_step)*0.5),zero=R(0.0*half);
    float acceleration_x=(float)zero,acceleration_y=(float)R(half*gravity),acceleration_w=(float)half;
    ThugSkaterBody *body=p->body;float dt=p->time_step;
    double dx=R((double)dt*body->velocity[0]);
    float dy=(float)R((double)dt*body->velocity[1]),dz=(float)R((double)dt*body->velocity[2]),dw=(float)R((double)dt*body->velocity[3]);
    float delta_x=(float)R(dx+acceleration_x),delta_y=(float)R((double)dy+acceleration_y);
    double delta_z=R(zero+dz),delta_w=R((double)dw+acceleration_w);
    body->position[0]=(float)R((double)delta_x+body->position[0]);body->position[1]=(float)R((double)delta_y+body->position[1]);
    body->position[2]=(float)R(delta_z+body->position[2]);body->position[3]=(float)R(delta_w+body->position[3]);
    thug_vector_add(p->body->position,displacement);
    body=p->body;dt=p->time_step;zero=R(0.0*dt);
    acceleration_x=(float)zero;acceleration_y=(float)R((double)dt*gravity);
    body->velocity[0]=(float)R((double)acceleration_x+body->velocity[0]);body->velocity[1]=(float)R((double)acceleration_y+body->velocity[1]);
    body->velocity[2]=(float)R(zero+body->velocity[2]);body->velocity[3]=(float)R((double)dt+body->velocity[3]);
    float *normal=p->wall_transition_normal;
    double tx=normal[2],ty=0,tz=negative(normal[0]);
    double length=R(__builtin_sqrt(R(R(tz*tz)+R(tx*tx))));
    if(length>0) {double scale=R(1/length);tx=R(tx*scale);ty=(float)R(0.0*scale);tz=R(tz*scale);}
    float turn_direction[4]={(float)R(R(ty*normal[2])-R(tz*normal[1])),(float)R(R(tz*normal[0])-R(tx*normal[2])),(float)R(R(tx*normal[1])-R(ty*normal[0])),0};
    float radians=(float)thug_script_get_global_number(0x64a48a64,1);body=p->body;
    double alignment=thug_vector_dot(turn_direction,body->orientation+8);
    if(!(alignment>0.68f)&&(!(alignment>0)||!(alignment>thug_platform_cos(radians)))) {
        if(thug_vector_dot(turn_direction,body->orientation)<=0)radians=negative(radians);
        body->velocity[3]=1;thug_vector_rotate_axis(p->body->velocity,normal,radians);
        thug_vector_copy(p->body->orientation+8,p->body->velocity);thug_vector_normalize(p->body->orientation+8);
        thug_vector_copy(p->body->orientation+4,normal);body=p->body;
        float right[4];thug_vector_cross(right,body->orientation+4,body->orientation+8);
        body->orientation[3]=0;body->orientation[2]=right[2];body->orientation[0]=right[0];body->orientation[1]=right[1];
        thug_vector_normalize(p->body->orientation);cache_orientation(p);
    }
    body=p->body;float direction[4];thug_vector_difference(direction,body->position,body->previous_position);normalize_zyx(direction);
    thug_vector_copy(p->surface_segment,body->previous_position);thug_vector_copy(p->surface_segment+4,p->body->position);
    double scan=thug_skater_get_parameter(0x20102726,1,p->body);add_scaled(p->surface_segment+4,direction,scan,1);
    const uint32_t exit_wall[3]={1,5,0},enter_wall[3]={1,3,0},jump_wall[3]={2,4,0};
    if(thug_skater_query_surface(p,0x10,0,q)) {
        float hit_normal[4];thug_vector_copy(hit_normal,p->surface_probe.normal);
        alignment=thug_vector_dot(hit_normal,normal);body=p->body;
        float corrected[4];for(unsigned i=0;i<4;++i)corrected[i]=(float)R((double)hit_normal[i]+p->surface_probe.point[i]);
        body->position[2]=corrected[2];body->position[3]=corrected[3];body->position[0]=corrected[0];body->position[1]=corrected[1];
        if(p->surface_flag_4&&!(__builtin_fabs(alignment)<0.01f)) {
            thug_vector_copy(normal,hit_normal);thug_skater_set_up_vector(p,normal[0],normal[1],normal[2],normal[3],q);
            cache_orientation(p);thug_vector_project_preserve_length(p->body->velocity,normal);
        } else if(hit_normal[1]>0.9f) {
            thug_vector_copy(p->body->position,p->surface_probe.point);thug_vector_copy(p->body->orientation+8,p->body->velocity);
            thug_vector_project_plane(p->body->orientation+8,hit_normal);thug_vector_normalize(p->body->orientation+8);
            thug_vector_copy(p->body->orientation+4,hit_normal);body=p->body;
            float right[4];thug_vector_cross(right,body->orientation+4,body->orientation+8);thug_vector_copy(body->orientation,right);
            thug_vector_normalize(p->body->orientation);cache_orientation(p);
            ThugObjectComponent *component=thug_object_find_component(p->body,0xbf518e27);
            thug_matrix_copy((float *)((uint8_t *)component+0x18),((ThugSkaterBody *)component->owner)->orientation);
            thug_vector_copy(p->orientation_previous,p->body->orientation+4);thug_vector_copy(p->orientation_source,p->body->orientation+4);thug_vector_copy(p->orientation_target,p->body->orientation+4);
            thug_skater_acquire_rail(p,1,q,d,m);if(p->state->mode==4)return;
            thug_skater_change_state(p,0,d,m);thug_object_emit_event((void *)p->body,0x532b16ef,0,d,m);return;
        } else move_away(p,q,0,d,m);
    }
    if(thug_skater_wall_overhang(p,q))move_away(p,q,0,d,m);
    body=p->body;double distance=thug_skater_get_parameter(0xe4d79235,1,parameter_body);
    segment_endpoint(p,p->surface_segment,body->orientation+4,distance);
    body=p->body;distance=thug_script_get_global_number(0x438ba168,1);segment_endpoint(p,p->surface_segment+4,body->orientation+4,distance);
    if(thug_skater_query_surface(p,0x10,0,q)) {
        thug_vector_copy(normal,p->surface_probe.normal);thug_vector_copy(p->body->position,p->surface_probe.point);
        thug_vector_add(p->body->position,normal);thug_vector_project_preserve_length(p->body->velocity,normal);
        thug_skater_set_up_vector(p,normal[0],normal[1],normal[2],normal[3],q);cache_orientation(p);
        if(!p->surface_flag_4) {
            add_scaled(p->body->velocity,normal,100,3);up(p,q);cache_orientation(p);leave_events(p,d,m);
            collision_event(p,exit_wall,d,m);if(interrupted(p))return;
        } else {
            if(p->surface_probe.result.instance!=p->saved_probe.result.instance) {
                collision_event(p,exit_wall,d,m);if(interrupted(p))return;
                collision_event(p,enter_wall,d,m);if(interrupted(p))return;
            }
            if(!((uint8_t *)p->name_context)[0x13b0])thug_skater_set_notification_flag(p->name_context,0,d,m);
            thug_collision_probe_assign(&p->saved_probe,&p->surface_probe);p->sound->unknown_1c[1]=p->saved_probe.result.surface_metadata;
        }
    } else {move_away(p,q,1,d,m);collision_event(p,exit_wall,d,m);if(interrupted(p))return;}
    if(!p->state->drag_coefficient_selector&&p->input->button_1c0.pressed)mark(p->state,0x20,1);
    if(thug_skater_handle_input_release(p,d,m)) {
        mark(p->state,0xd8,1);collision_event(p,jump_wall,d,m);if(interrupted(p))return;
        double jump=thug_script_get_global_number(0x349d02d4,1);add_scaled(p->body->velocity,normal,jump,1);
        float *vertical=p->body->velocity+1;jump=thug_script_get_global_number(0x5a9de35a,1);*vertical=(float)R(jump+*vertical);
        float *axis=p->body->orientation+4;axis[1]=axis[3]=1;axis[0]=axis[2]=0;
        thug_matrix_orthogonalize(p->body->orientation,1);cache_orientation(p);p->orientation_blend=0;
        thug_vector_copy(p->orientation_source,p->body->orientation+4);thug_vector_copy(p->orientation_target,p->orientation_source);thug_vector_copy(p->orientation_previous,p->orientation_source);
    }
    thug_skater_notify(p->name_context,p->saved_probe.result.checksum,d,m);
}

#undef R
