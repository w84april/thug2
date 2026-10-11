#include "skater.h"
#include "stats.h"
#include "balance.h"
#include "../audio/events.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../core/number.h"
#include "../network/queue.h"
#include "../script/schedule.h"
#include "../script/tokens.h"
#include "../platform/math.h"
#include <stddef.h>
#define R thug_platform_round_x87_single

_Static_assert(sizeof(ThugAxisRotation)==0x18,"Axis rotation record");
_Static_assert(sizeof(ThugAxisRotationQueue)==0x94,"Axis rotation queue");
_Static_assert(offsetof(ThugRotationComponent,axes)==0x38,"Rotation axes");
_Static_assert(offsetof(ThugSkaterPhysics,rotation_input_used)==0x2db,"Rotation input gate");
_Static_assert(offsetof(ThugSkaterPhysics,rotation_duration)==0x2e0,"Rotation duration");
_Static_assert(offsetof(ThugSkaterPhysics,rotation_requested)==0x3a4,"Rotation request");
static uint32_t float_bits(float value) { uint32_t bits;__builtin_memcpy(&bits,&value,4);return bits; }

_Static_assert(offsetof(ThugSkaterNameContext,spin_angle)==0x13a4,"Cumulative spin angle");
_Static_assert(offsetof(ThugSkaterPhysics,tap_turn_mode)==0x2da,"Tap turn mode");
_Static_assert(offsetof(ThugSkaterPhysics,tap_turn_remaining)==0x30c,"Remaining tap turn");
_Static_assert(offsetof(ThugSkaterPhysics,spin_input_blocked)==0x370,"Spin input gate");
_Static_assert(offsetof(ThugSkaterPhysics,score_component)==0x1520,"Spin score component");

static void cancel_auto_turn(ThugSkaterState *state) {
    if(state->transition_flag_68) {
        state->transition_flag_68=0;
        state->transition_time_6c=thug_elapsed_time()+thug_timer_offset;
    }
}

/* 0x00504060. Shoulder ages use unsigned FILD correction; directional ages
 * intentionally remain signed. Tap turns retain the full rate on overshoot.
 * Score/UI/QB execution follows the two independent orientation updates. */
void thug_skater_spin_input(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    ThugSkaterInput *input=p->input;
    ThugSkaterBody *parameter_body=p->body;
    if(p->spin_input_blocked)return;
    ThugSkaterState *state=p->state;
    if(state->skip_ground_probe)cancel_auto_turn(state);
    float rate=0;uint32_t elapsed=0;int shoulder_active=0;
    if(p->tap_turn_mode) {
        if(input->button_a0.pending_10) {
            thug_input_button_clear_latch(&input->button_a0);
            if(!input->button_100.pressed)
                p->tap_turn_remaining=(float)R((double)p->tap_turn_remaining+3.1415927410125732f);
        }
        if(input->button_100.pending_10) {
            thug_input_button_clear_latch(&input->button_100);
            if(!input->button_a0.pressed)
                p->tap_turn_remaining=(float)R((double)p->tap_turn_remaining-3.1415927410125732f);
        }
        if(p->tap_turn_remaining!=0) {
            shoulder_active=1;
            float sign=p->tap_turn_remaining<0?-1:1;
            double wide_rate=R(thug_skater_stat_parameter(p->body,0xf7a2acc1)*sign);
            double delta=R(wide_rate*p->time_step);
            if(__builtin_fabs((double)p->tap_turn_remaining)<__builtin_fabs(delta))p->tap_turn_remaining=0;
            else p->tap_turn_remaining=(float)R((double)p->tap_turn_remaining-delta);
            rate=(float)wide_rate;
        }
    } else {
        ThugInputButton *left=&input->button_a0,*right=&input->button_100;
        if(left->pressed&&!right->pressed) {
            float age=(float)thug_input_button_elapsed(left);
            if(thug_skater_get_parameter(0xa5a02449,0,0)<age) {
                rate=(float)thug_skater_stat_parameter(p->body,0x4957db43);
                shoulder_active=1;age=(float)thug_input_button_elapsed(left);
                if(thug_skater_get_parameter(0xabdd3395,1,parameter_body)<age)cancel_auto_turn(p->state);
            }
        }
        if(right->pressed&&!left->pressed) {
            float age=(float)thug_input_button_elapsed(right);
            if(thug_skater_get_parameter(0xa5a02449,0,0)<age) {
                rate=(float)-thug_skater_stat_parameter(p->body,0x4957db43);
                shoulder_active=1;age=(float)thug_input_button_elapsed(right);
                if(thug_skater_get_parameter(0xabdd3395,1,parameter_body)<age)cancel_auto_turn(p->state);
            }
        }
    }
    if(!p->state->state_flag_c0&&!shoulder_active) {
        if(input->button_60.pressed) {
            rate=(float)thug_skater_stat_parameter(p->body,0x4957db43);
            elapsed=thug_input_button_elapsed(&input->button_60);
            float age=(float)(int32_t)elapsed;
            if(thug_skater_get_parameter(0xabdd3395,1,parameter_body)<age)cancel_auto_turn(p->state);
        }
        if(input->button_80.pressed) {
            rate=(float)-thug_skater_stat_parameter(p->body,0x4957db43);
            elapsed=thug_input_button_elapsed(&input->button_80);
            float age=(float)(int32_t)elapsed;
            if(thug_skater_get_parameter(0xabdd3395,1,parameter_body)<age)cancel_auto_turn(p->state);
        }
        float cutoff=(float)thug_skater_get_parameter(0xa092b2be,1,parameter_body);
        double endpoint=thug_skater_get_parameter(0x5d756349,1,parameter_body);
        double time=(int32_t)elapsed;
        if(time<=cutoff)rate=0;
        if(time<endpoint)rate=(float)R(R(R(time-cutoff)*rate)/R(endpoint-cutoff));
    }
    if(rate==0) {
        state=p->state;
        if(state->ground_transition_flag&&state->transition_flag_68) {
            float vertical=(float)thug_clamp_number(p->body->orientation[9],-1,1);
            float angle=(float)thug_platform_acos_x87_single(vertical);
            double threshold=R(thug_skater_get_parameter(0x61224f2e,1,parameter_body)*.01745329238474369f);
            if(threshold>angle)cancel_auto_turn(p->state);
            else {
                ThugSkaterBody *body=p->body;
                angle=(float)thug_vector_signed_angle(body->orientation+8,p->transition_forward,body->orientation+4);
                float speed=(float)thug_skater_get_parameter(0x9db33213,1,parameter_body);
                double wide_rate=R(thug_sign_nonnegative(angle)*speed);
                rate=(float)wide_rate;
                if(__builtin_fabs((double)angle)<__builtin_fabs(R(wide_rate*p->time_step))) {
                    rate=(float)R((double)angle/p->time_step);
                    cancel_auto_turn(p->state);
                }
            }
        }
        if(rate==0)return;
    }
    p->turn_positive=rate>0;
    float delta=(float)R((double)rate*p->time_step),rotation[16];
    float *target=p->body->orientation;
    thug_matrix_rotation_y(rotation,delta);thug_matrix_multiply(target,rotation,target);
    thug_matrix_rotation_y(rotation,delta);thug_matrix_multiply(p->cached_orientation,rotation,p->cached_orientation);
    ThugSkaterNameContext *context=p->name_context;
    context->spin_angle=(float)R(R((double)delta*57.2957763671875f)+context->spin_angle);
    state=p->state;
    if(state->ground_transition_flag&&!state->skip_ground_probe) {
        float magnitude=__builtin_fabsf(p->name_context->spin_angle);
        double threshold=R(R(360-thug_skater_get_parameter(0x50c5cc2f,1,parameter_body))+.10000000149011612f);
        if(!(threshold<=magnitude))return;
    }
    uint32_t angle=thug_truncate_low_word(p->name_context->spin_angle);
    thug_score_update_spin_if_trick(p->score_component->score,(int32_t)angle,d,m);
}

/* 0x00420520. Queue raw words so signaling NaNs and padding are unchanged.
 * The first unoccupied record wins; a full queue does not change its flag. */
void thug_rotation_queue_add(ThugAxisRotationQueue *queue,uint32_t duration,uint32_t time,
    uint32_t start,uint32_t delta,uint32_t mode,uint32_t flag,uint32_t secondary) {
    for(uint32_t i=0;i<6;++i) {
        ThugAxisRotation *entry=&queue->entries[i];
        if(entry->flags&1)continue;
        entry->duration_bits=duration;entry->time=time;entry->start_bits=start;
        entry->delta_bits=delta;entry->mode=mode;
        entry->flags=(entry->flags&0xf9)|1|((flag&1)<<1)|((secondary&1)<<2);
        queue->active=1;return;
    }
}

/* 0x00420730. Schedule each selected axis and broadcast for a local player.
 * The original packet's final byte is unwritten stack padding; define it as
 * zero, consistent with the other recovered network packets. */
void thug_rotation_schedule(ThugRotationComponent *rotation,float duration,float start,float endpoint,
    uint32_t mode,uint32_t flag,uint32_t x,uint32_t y,uint32_t z,
    const ThugDiagnostics *d,const ThugMemory *m) {
    duration=(float)R((double)duration*16.66666603088379f);
    rotation->pivot[0]=0;rotation->pivot[1]=30;rotation->pivot[2]=0;rotation->pivot[3]=1;
    uint32_t now=thug_elapsed_time()+thug_timer_offset;
    uint32_t selectors[3]={x,y,z},mask=0;
    for(uint32_t i=0;i<3;++i)if((uint8_t)selectors[i]) {
        float delta=(float)R((double)endpoint-start);
        thug_rotation_queue_add(rotation->axes+i,float_bits(duration),now,float_bits(start),float_bits(delta),mode,flag,0);
        mask|=1u<<i;
    }
    const ThugSkaterBody *owner=rotation->base.owner;
    ThugNetworkState *network=thug_network_state;
    ThugPlayerState *player=thug_player_find(network,owner->object_id);
    if(player&&(uint8_t)thug_player_flag_1(player)) {
        ThugMessageSpec spec;thug_message_spec_initialize(&spec);
        ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
        uint8_t payload[16];
        thug_script_write_word(payload,thug_truncate_low_word(duration));
        thug_script_write_half(payload+8,(uint16_t)thug_truncate_low_word(start));
        thug_script_write_half(payload+10,(uint16_t)thug_truncate_double_low_word(R((double)endpoint-start)));
        thug_script_write_word(payload+4,mode);
        owner=rotation->base.owner;payload[12]=(uint8_t)owner->object_id;
        payload[13]=(uint8_t)flag;payload[14]=(uint8_t)mask;payload[15]=0;
        spec.data=payload;spec.length=16;spec.id=0x76;
        thug_queue_send_first(client,&spec,d,m);
    }
}

/* 0x004208d0. Clear every axis before the optional one-byte network notice. */
void thug_rotation_clear(ThugRotationComponent *rotation,const ThugDiagnostics *d,const ThugMemory *m) {
    for(unsigned axis=0;axis<3;++axis) {
        for(unsigned entry=0;entry<6;++entry)rotation->axes[axis].entries[entry].flags&=0xfc;
        rotation->axes[axis].active=0;
    }
    const ThugSkaterBody *body=rotation->base.owner;
    ThugNetworkState *network=thug_network_state;
    ThugPlayerState *player=thug_player_find(network,body->object_id);
    if(player&&(uint8_t)thug_player_flag_1(player)) {
        ThugMessageSpec spec;thug_message_spec_initialize(&spec);
        ThugQueueClient *client=thug_network_get_client(network,thug_player_network_index(player));
        body=rotation->base.owner;uint8_t id=(uint8_t)body->object_id;
        spec.data=&id;spec.length=1;spec.id=0x8c;
        thug_queue_send_first(client,&spec,d,m);
    }
}

/* 0x004ffb90. Required checksum pairs come from the loaded rotation table.
 * The first matching entry schedules its axes and runs the real QB handler. */
void thug_skater_check_rotation_input(ThugSkaterPhysics *p,const ThugDiagnostics *d,const ThugMemory *m) {
    if(p->state->resistance_requested||p->rotation_input_used)return;
    ThugSkaterInput *input=p->input;
    if(!input->button_160.pressed&&!input->button_180.pressed)return;
    p->rotation_half_turn=0;
    ThugSkaterNameContext *history=(void *)thug_object_find_component(p->body,0x270f56e1);
    ThugScriptArray *array=thug_script_get_global_array(0xb75d73e5,0);
    int32_t count=(int32_t)array->count;
    for(int32_t i=0;i<count;++i) {
        ThugScriptStructure *entry=thug_script_array_structure(array,i);uint32_t keys[3];
        thug_script_get_checksum(entry,0x24715af5,keys,0);
        thug_script_get_checksum(entry,0xbd780b4f,keys+1,0);
        keys[2]=input->button_160.pressed?0x2b489a86:0x321c9756;
        if(!thug_skater_match_rotation_input(history,keys,p->ground_flag_2e4))continue;
        p->rotation_input_used=1;p->rotation_duration=50;p->rotation_requested=1;p->ground_flag_2e4=1;
        ThugRotationComponent *rotation=(void *)thug_object_find_component(p->body,0x286a8d26);
        uint32_t angles[3]={0,0,0};
        static const uint32_t names[3]={0x0affd09d,0x7df8e00b,0xe4f1b1b1};
        for(uint32_t axis=0;axis<3;++axis)if(thug_script_get_integer(entry,names[axis],angles+axis,0)&&angles[axis]) {
            if(axis==1&&(angles[axis]==180||angles[axis]==(uint32_t)-180))p->rotation_half_turn=1;
            thug_rotation_schedule(rotation,p->rotation_duration,0,(float)(int32_t)angles[axis],0,1,axis==0,axis==1,axis==2,d,m);
        }
        thug_script_run_sync(0xd8fa65d7,entry,(ThugReferencedObject *)p->body,0,d,m);
        return;
    }
}

/* 0x004ffdb0. Scan vertically at the current position, then test a raised path
 * from the supplied previous point. The temporary moving reference is released
 * on every constructed-probe path, including rejected normals and obstructions. */
uint8_t thug_skater_try_raised_path(ThugSkaterPhysics *p,const float previous[4],
    ThugCollisionQuery *query) {
    if(p->state->resistance_requested)return 0;
    ThugCollisionProbe probe;
    thug_collision_probe_initialize(&probe);
    float height=(float)thug_skater_get_parameter(0x786b3272,1,p->body);
    const float *position=p->body->position;
    thug_vector_copy(probe.segment,position);
    probe.segment[1]=(float)R((double)position[1]+height);
    thug_vector_copy(probe.segment+4,position);
    if(previous[1]<position[1])probe.segment[5]=previous[1];
    double raised=R((double)height+previous[1]);
    if(raised>probe.segment[1])probe.segment[1]=(float)raised;
    uint8_t accepted=0;
    if(thug_collision_probe_query(&probe,1,0,query)&&probe.normal[1]>.5f) {
        float landing[4];
        landing[0]=(float)R((double)probe.normal[0]+probe.point[0]);
        landing[1]=(float)R((double)probe.point[1]+probe.normal[1]);
        landing[2]=(float)R((double)probe.normal[2]+probe.point[2]);
        landing[3]=(float)R((double)probe.normal[3]+probe.point[3]);
        thug_vector_copy(probe.segment,previous);
        probe.segment[1]=(float)R((double)previous[1]+height);
        thug_vector_copy(probe.segment+4,landing);
        probe.segment[5]=(float)R((double)landing[1]+height);
        if(!thug_collision_probe_query(&probe,1,0,query)) {
            thug_vector_copy(p->body->position,landing);
            float *current=p->body->position;
            current[1]=(float)R((double)current[1]+.10000000149011612f);
            accepted=1;
        }
    }
    thug_collision_probe_release(&probe);
    return accepted;
}

/* 0x00504ee0. The second query replaces the retained probe, but the velocity
 * projection must keep the FIRST normal. Offset X/Y retain their wide exponent
 * until their sums spill; Z/W spill before the corresponding additions. */
uint8_t thug_skater_resolve_overhead(ThugSkaterPhysics *p,ThugCollisionQuery *query) {
    if(p->body->orientation[5]<0)return 0;
    float height=(float)thug_skater_get_parameter(0x542cf0c7,1,p->body);
    uint32_t timestamp=p->rebound_gate_time;
    uint32_t age=thug_elapsed_time()+thug_timer_offset-timestamp;
    if(age<=thug_script_get_global_integer(0x2757ed2c,0))height=6;
    const float *body_up=p->body->orientation+4;
    double x=R((double)height*body_up[0]),y=R((double)height*body_up[1]);
    float z=(float)R((double)height*body_up[2]),w=(float)R((double)height*body_up[3]);
    thug_vector_copy(p->surface_segment,p->body->position);
    thug_vector_copy(p->surface_segment+4,p->body->position);
    p->surface_segment[4]=(float)R(x+p->surface_segment[4]);
    p->surface_segment[5]=(float)R(y+p->surface_segment[5]);
    p->surface_segment[6]=(float)R((double)z+p->surface_segment[6]);
    p->surface_segment[7]=(float)R((double)w+p->surface_segment[7]);
    if(!thug_skater_query_surface(p,0x10,0,query))return 0;
    float normal[4];thug_vector_copy(normal,p->surface_probe.normal);
    if(normal[1]>-.10000000149011612f)return 0;
    float difference[4];
    thug_vector_difference(difference,p->surface_probe.point,p->surface_segment+4);
    thug_vector_project_axis(difference,normal);
    thug_vector_copy(p->surface_segment,p->body->position);
    const float *position=p->body->position;
    x=R((double)difference[0]+position[0]);y=R((double)difference[1]+position[1]);
    z=(float)R((double)difference[2]+position[2]);w=(float)R((double)difference[3]+position[3]);
    p->surface_segment[6]=z;p->surface_segment[7]=w;
    p->surface_segment[4]=(float)x;p->surface_segment[5]=(float)y;
    if(thug_skater_query_surface(p,0x10,0,query)) {
        float offset[4],adjusted[4];
        thug_vector_scaled(offset,.0010000000474974513f,p->surface_probe.normal);
        thug_vector_sum(adjusted,p->surface_probe.point,offset);
        thug_vector_copy(p->body->position,adjusted);
    } else thug_vector_copy(p->body->position,p->surface_segment+4);
    thug_vector_project_plane(p->body->velocity,normal);
    return 1;
}

/* 0x004fc470. Material events may replace either live component. */
void thug_skater_set_material(ThugSkaterPhysics *p,uint32_t material,
    const ThugDiagnostics *d,const ThugMemory *m) {
    thug_skater_state_set_material(p->state,material,d,m);
    p->sound->unknown_1c[0]=(uint8_t)material;
}

/* 0x00504910. The first elapsed comparison uses the exact signed FILD value;
 * subsequent ramp arithmetic reloads its float spill. The second button wins. */
void thug_skater_pitch_input(ThugSkaterPhysics *p) {
    if(p->state->skip_ground_probe||p->state->state_flag_c0||p->state->ground_transition_flag)return;
    ThugSkaterInput *input=p->input;
    if(input->button_160.pressed||input->button_180.pressed)return;
    float rate=0;uint32_t elapsed=0;
    if(input->button_20.pressed) {
        rate=(float)thug_skater_stat_parameter(p->body,0xcbfdd841);
        elapsed=thug_input_button_elapsed(&input->button_20);
    }
    if(input->button_40.pressed) {
        rate=(float)-thug_skater_stat_parameter(p->body,0xcbfdd841);
        elapsed=thug_input_button_elapsed(&input->button_40);
    }
    float cutoff=(float)thug_script_get_global_number(0x5f70ef46,1);
    float endpoint=(float)thug_script_get_global_number(0x12cd2d14,1);
    double signed_elapsed=(int32_t)elapsed;
    float time=(float)signed_elapsed;
    if(signed_elapsed<=cutoff)return;
    if(time<endpoint)rate=(float)R(R(R((double)time-cutoff)*rate)/R((double)endpoint-cutoff));
    thug_matrix_rotate_x(p->body->orientation,(float)R((double)rate*p->time_step));
    thug_matrix_rotate_x(p->cached_orientation,(float)R((double)rate*p->time_step));
}

/* 0x00504a60. Smooth the transfer fraction, apply its incremental rotation,
 * then retain the current absolute orientation for the next frame. */
void thug_skater_transfer_orientation(ThugSkaterPhysics *p) {
    if(!p->state->skip_ground_probe)return;
    double progress=R((double)p->time_step+p->transfer_progress);
    p->transfer_progress=(float)progress;
    double t=R(progress/p->transfer_duration);
    if(t>1)t=1;
    float eased=(float)R(R(R(R(t-1.5)*t)*t)*-2);
    float current[16],previous_inverse[16],delta[16];
    thug_matrix_interpolate(&p->transfer_interpolation,current,eased);
    thug_matrix_copy(previous_inverse,p->transfer_previous_orientation);
    thug_matrix_rigid_inverse(previous_inverse);
    thug_matrix_multiply(delta,previous_inverse,current);
    thug_matrix_multiply(p->body->orientation,p->body->orientation,delta);
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
    thug_matrix_copy(p->transfer_previous_orientation,current);
}

/* 0x00504df0. Keep the zero product: an unordered up vector cannot be simplified
 * to a finite horizontal cross product. Threshold equality performs no turn. */
void thug_skater_upright_orientation(ThugSkaterPhysics *p) {
    const float *basis=p->body->orientation;
    if(__builtin_fabsf(basis[9])>.949999988079071f)return;
    double correction=R(R(R(-(double)basis[10]*basis[4])+R((double)basis[8]*basis[6]))+R((double)basis[5]*0));
    int sign;
    if(correction>R((double)p->time_step*1.1999999284744263f))sign=1;
    else if(correction<R((double)p->time_step*-1.1999999284744263f))sign=-1;
    else return;
    double angle=R(R(thug_script_get_global_number(0xabd57877,0)*.01745329238474369f)*p->time_step);
    float rotation[16];
    float *target=p->body->orientation;
    thug_matrix_rotation_z(rotation,(float)(sign<0?-angle:angle));
    thug_matrix_multiply(target,rotation,target);
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
}
