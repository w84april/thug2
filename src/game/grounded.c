#include "skater.h"
#include "balance.h"
#include "attachment.h"
#include "moving_contact.h"
#include "objectives.h"
#include "../audio/events.h"
#include "../core/number.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterPhysics,ground_value_22c)==0x22c,"Ground scratch");
_Static_assert(offsetof(ThugSkaterPhysics,ground_value_244)==0x244,"Ground scratch");
_Static_assert(offsetof(ThugSkaterPhysics,ground_flag_2e4)==0x2e4,"Ground flag");
_Static_assert(offsetof(ThugSkaterPhysics,heading)==0x348,"Ground heading");
_Static_assert(offsetof(ThugSkaterPhysics,ground_gravity_override)==0x360,"Ground gravity");
_Static_assert(offsetof(ThugSkaterPhysics,ground_flag_4e8)==0x4e8,"Ground flag");
_Static_assert(offsetof(ThugSkaterPhysics,saved_probe.result.checksum)==0x1b0,"Ground event key");

static double length3(double x,double y,double z) {
    return R(__builtin_sqrt(R(R(R(x*x)+R(y*y))+R(z*z))));
}
static void timed_flag(ThugSkaterState *state,unsigned offset,uint8_t value) {
    uint8_t *flag=(uint8_t *)state+offset;
    if(*flag!=value) {
        *flag=value;
        uint32_t time=thug_elapsed_time()+thug_timer_offset;
        __builtin_memcpy(flag+4,&time,4);
    }
}
static ThugBalance *balance(ThugSkaterModeContext *mode,unsigned offset) {
    return (ThugBalance *)((uint8_t *)mode+offset);
}
/* 0x0050ee70. Complete grounded frame, including the single remaining-distance
 * retry. Script/event calls may replace components: keep the original re-reads.
 * The original caller supplies live components and valid balance/attachment data. */
void thug_skater_update_grounded(ThugSkaterPhysics *p,ThugCollisionQuery *query,
    const ThugDiagnostics *d,const ThugMemory *m) {
    const unsigned flags[]={0x48,0x30,0x38,0x78,0xa8,0x80,0xb0};
    for(unsigned i=0;i<7;i++)timed_flag(p->state,flags[i],0);
    p->ground_value_22c=0;p->ground_value_244=0;p->ground_flag_4e8=0;
    p->ground_transition_flag=0;p->ground_flag_2e4=0;p->wall_transition_value=0;
    double heading=R(thug_acos_approximate(p->body->orientation[8])*57.2957763671875);
    p->heading=(float)heading;
    if(p->body->orientation[10]<0)p->heading=(float)R(360-heading);
    float *velocity=p->body->velocity;
    if(length3(velocity[0],velocity[1],velocity[2])>(double).0010000000474974513f)
        thug_vector_project_preserve_length(velocity,p->orientation_target);
    float gravity=(float)thug_skater_get_parameter(0x6618a713,1,p->body);
    if(p->drag_override_active!=0&&p->body->velocity[1]>0)gravity=p->ground_gravity_override;
    float acceleration[4]={0,gravity,0,1};
    thug_vector_project_plane(acceleration,p->orientation_target);
    double x=R((double)p->time_step*acceleration[0]);
    float y=(float)R((double)p->time_step*acceleration[1]);
    float z=(float)R((double)p->time_step*acceleration[2]);
    float w=(float)R((double)p->time_step*acceleration[3]);
    velocity=p->body->velocity;
    velocity[0]=(float)R(x+velocity[0]);velocity[1]=(float)R((double)y+velocity[1]);
    velocity[2]=(float)R((double)z+velocity[2]);velocity[3]=(float)R((double)w+velocity[3]);
    p->alternate_acceleration=0;
    uint32_t mode=p->mode_context->identifier;
    if(mode==0) {
        if(thug_skater_should_brake(p))thug_skater_brake(p);
        else { p->braking=0;if(thug_skater_can_accelerate(p))thug_skater_accelerate(p); }
    } else if(mode==0x3506ce64) {
        thug_balance_update(balance(p->mode_context,0x12c),d,m);
        if(thug_gameplay_flag(thug_game_context->gameplay_flags,0x69a1ce96)) {
            ThugGameplayFlags *game_flags=thug_game_context->gameplay_flags;
            thug_gameplay_flag_set(game_flags,thug_script_get_global_integer(0x69a1ce96,0));
            balance(p->mode_context,0x12c)->position=0;
            balance(p->mode_context,0x12c)->velocity=0;thug_last_gameplay_flag=1;
        }
    } else if(mode==0x0ac90769||mode==0xef24413b) {
        p->braking=0;
        if(p->parameter_mode_fallback) {
            p->alternate_acceleration=1;
            if(thug_skater_can_accelerate(p))thug_skater_accelerate(p);
        }
        thug_balance_update(balance(p->mode_context,0x24),d,m);
        thug_skater_set_notification_flag(p->name_context,1,d,m);
        if(thug_gameplay_flag(thug_game_context->gameplay_flags,0xb38341c9)) {
            ThugGameplayFlags *game_flags=thug_game_context->gameplay_flags;
            thug_gameplay_flag_set(game_flags,thug_script_get_global_integer(0xb38341c9,0));
            balance(p->mode_context,0x24)->position=0;
            balance(p->mode_context,0x24)->velocity=0;thug_last_gameplay_flag=1;
        }
    }
    thug_skater_apply_resistance(p);thug_skater_apply_repulsion(p,query);
    float delta[4];
    for(unsigned i=0;i<4;i++)delta[i]=(float)R((double)p->time_step*p->body->velocity[i]);
    if(p->state->moving_contact_locked) {
        ThugMovingContact *contact=p->ground_gate->contact;
        if(contact&&contact->reference.object) {
            ThugSkaterBody *owner=(ThugSkaterBody *)contact->reference.object;
            double scale=thug_script_get_global_number(0xdef25b34,1);
            double vx=R(scale*owner->velocity[0]),vy=R(scale*owner->velocity[1]);
            float vz=(float)R(scale*owner->velocity[2]),vw=(float)R(scale*owner->velocity[3]);
            velocity=p->body->velocity;
            velocity[2]=vz;velocity[3]=vw;velocity[0]=(float)vx;velocity[1]=(float)vy;
        }
        delta[0]=delta[1]=delta[2]=0;delta[3]=1;
        thug_skater_update_attachment(p,d,m);
    }
    ThugSkaterGroundGate *gate=p->ground_gate;
    ThugMovingContact *contact=gate->contact;
    if(contact) {
        if(!contact->reference.object||!thug_moving_contact_update(contact,p->body->position))
            thug_skater_moving_contact_release(gate,m);
        else if(!p->state->moving_contact_locked) {
            contact=p->ground_gate->contact;
            float *position=p->body->position;
            for(unsigned i=0;i<4;i++)position[i]=(float)R((double)contact->displacement[i]+position[i]);
            thug_vector_copy(p->body->previous_position,p->body->position);
            thug_vector_copy(p->side_previous_position,p->body->position);
            contact=p->ground_gate->contact;
            if(contact->orientation_changed) {
                thug_matrix_multiply(p->body->orientation,p->body->orientation,contact->rotation);
                thug_matrix_multiply(p->cached_orientation,p->cached_orientation,p->ground_gate->contact->rotation);
            }
        }
    }
    uint8_t retried=0;
    for(;;) {
        float *position=p->body->position;
        float before[3]={position[0],position[1],position[2]};
        for(unsigned i=0;i<4;i++)position[i]=(float)R((double)delta[i]+position[i]);
        if(!p->state->moving_contact_locked)thug_skater_movement_sweep(p,query,d,m);
        if(!p->state->moving_contact_locked)thug_skater_handle_floor(p,query,d,m);
        else {
            /* X products stay unspilled; the other products spill before sums. */
            for(unsigned endpoint=0;endpoint<2;endpoint++) {
                ThugSkaterBody *body=p->body;double scale=endpoint?200:36;
                double vx=R((double)body->orientation[4]*scale);
                float vy=(float)R((double)body->orientation[5]*scale);
                float vz=(float)R((double)body->orientation[6]*scale);
                float vw=(float)R((double)body->orientation[7]*scale);
                double rx=endpoint?R((double)body->position[0]-vx):R(vx+body->position[0]);
                double ry=endpoint?R((double)body->position[1]-vy):R((double)vy+body->position[1]);
                float rz=(float)(endpoint?R((double)body->position[2]-vz):R((double)vz+body->position[2]));
                float rw=(float)(endpoint?R((double)body->position[3]-vw):R((double)vw+body->position[3]));
                float *out=p->surface_probe.segment+endpoint*4;
                out[2]=rz;out[3]=rw;out[0]=(float)rx;out[1]=(float)ry;
            }
            if(thug_skater_query_surface(p,0x10,0,query)) {
                uint8_t material=p->surface_probe.result.surface_metadata;
                thug_skater_state_set_material(p->state,material,d,m);p->sound->unknown_1c[0]=material;
            }
        }
        ThugSkaterBody *body=p->body;
        double dx=R((double)body->position[0]-before[0]),dy=R((double)body->position[1]-before[1]),dz=R((double)body->position[2]-before[2]);
        double moved=length3(dx,dz,dy);
        float intended=(float)length3(delta[2],delta[1],delta[0]);
        if(retried||p->state->mode||!(moved<R((double)intended-(double).10000000149011612f)))break;
        double vx=body->velocity[0],vy=body->velocity[1];
        float vz=body->velocity[2],vw=body->velocity[3];
        double length=length3(vz,vy,vx);
        if(length>0) { double inverse=R(1/length);vx=R(vx*inverse);vy=R(vy*inverse);vz=(float)R((double)vz*inverse); }
        retried=1;
        float scaled_x=(float)R(vx*intended),scaled_w=(float)R((double)vw*intended);
        double scaled_y=R(vy*intended),scaled_z=R((double)vz*intended);
        double remaining=R(1-R(moved/intended));float stored_remaining=(float)remaining;
        delta[0]=(float)R(remaining*scaled_x);delta[1]=(float)R(scaled_y*stored_remaining);
        delta[2]=(float)R(scaled_z*stored_remaining);delta[3]=(float)R((double)scaled_w*stored_remaining);
    }
    if(p->state->mode)return;
    if(!p->unknown_2d8)thug_skater_steer(p);
    if(!p->accelerate_along_velocity)thug_skater_align_velocity(p,p->body->velocity);
    if(!p->state->moving_contact_locked) {
        thug_skater_correct_sides(p,query,d,m);thug_skater_correct_low_speed_collision(p,query);
    }
    if(!p->accelerate_along_velocity)thug_skater_handle_backward_motion(p,d,m);
    if(thug_skater_handle_input_release(p,d,m)) {
        thug_skater_prepare_floor_transition(p,query,d);
        timed_flag(p->state,0x48,1);timed_flag(p->state,0xd8,1);
    }
    thug_skater_notify(p->name_context,p->saved_probe.result.checksum,d,m);p->state_value_30c=0;
}
