/* 00504730: point-rail balance/spin state. */
#include "skater.h"
#include "grind.h"
#include "objectives.h"
#include "../core/timing.h"
#include "../core/number.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
void thug_skater_update_natas(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    (void)q;
    if(thug_gameplay_flag(thug_game_context->gameplay_flags,0xcd09e062)) {
        ThugGameplayFlags *flags=thug_game_context->gameplay_flags;
        thug_gameplay_flag_set(flags,thug_script_get_global_integer(0xcd09e062,0));
        ((ThugBalance *)((uint8_t *)p->mode_context+0xd4))->position=0;
        ((ThugBalance *)((uint8_t *)p->mode_context+0xd4))->velocity=0;
        thug_last_gameplay_flag=1;
    }
    thug_balance_update((void *)((uint8_t *)p->mode_context+0xd4),d,m);
    float maximum=(float)thug_script_get_global_number(0x6a94598a,1);
    double position=__builtin_fabs(thug_balance_position((void *)p->mode_context));
    double rate=R(R((double)maximum-R(position/R(4000.0/maximum)))+5);
    if(((uint8_t *)p)[0x1500])rate=-rate;
    p->turn_positive=rate>0;
    float angle=(float)R(rate*p->time_step),rotation[16];
    float *target=p->body->orientation;
    thug_matrix_rotation_y(rotation,angle);thug_matrix_multiply(target,rotation,target);
    thug_matrix_rotation_y(rotation,angle);thug_matrix_multiply(p->cached_orientation,rotation,p->cached_orientation);
    ThugSkaterNameContext *context=p->name_context;
    context->spin_angle=(float)R(R((double)angle*57.2957763671875f)+context->spin_angle);
    ThugSkaterState *state=p->state;
    uint8_t score=1;
    if(state->ground_transition_flag&&!state->skip_ground_probe) {
        float magnitude=__builtin_fabsf(p->name_context->spin_angle);
        double threshold=R(R(360-thug_skater_get_parameter(0x50c5cc2f,1,p->body))+.10000000149011612f);
        score=threshold<=magnitude;
    }
    if(score)thug_score_update_spin_if_trick(p->score_component->score,(int32_t)thug_truncate_low_word(p->name_context->spin_angle),d,m);
    uint32_t now=thug_elapsed_time()+thug_timer_offset;__builtin_memcpy((uint8_t *)p+0x1504,&now,4);
}
#undef R

#undef R

/* 0050c200: connected-rail transition recovery. */
#include "rail.h"
#include "stats.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../script/delivery.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
void thug_skater_transition_rail(ThugSkaterPhysics *p,const float prior[4],ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    float from[4],to[4],point[4];
    if(thug_skater_orientation_context->identifier==0xd443a2bc) {
        ThugSkaterBody *body=p->body;double dt=p->time_step;
        for(unsigned i=0;i<4;++i) {
            double product=R(dt*body->velocity[i]);if(i<3)product=(float)product;
            from[i]=(float)R((double)body->position[i]-product);
        }
    } else thug_vector_copy(from,prior);
    thug_vector_copy(to,p->body->position);from[1]=(float)R((double)from[1]+6);to[1]=(float)R((double)to[1]+6.099999904632568f);
    float degrees=(float)thug_script_get_global_number(0x76c1da15,1);
    int32_t side=thug_rail_side(p->rail_node,p->body->velocity,q);
    float alignment=(float)thug_platform_cos(R((double)degrees*.01745329238474369f));
    ThugRailNode *selected,*end;
    if(!thug_rail_search(p->rail_transform,from,to,point,&selected,p->rail_node,alignment,side,q)||!selected||selected==p->rail_node||!(end=selected->next))goto leave;
    if(thug_skater_orientation_context->identifier!=0xd443a2bc&&(p->rail_node->next==selected||p->rail_node->previous==selected))goto leave;
    float start_point[4],end_point[4],relative_start[4],relative_end[4];
    thug_rail_point(p->rail_transform,start_point,selected);thug_vector_difference(relative_start,start_point,p->body->position);
    thug_rail_point(p->rail_transform,end_point,end);thug_vector_difference(relative_end,end_point,p->body->position);
    double endpoint_dot=R(R(R((double)relative_end[0]*relative_start[0])+R((double)relative_end[2]*relative_start[2]))+R((double)relative_end[1]*relative_start[1]));
    float stored_dot=(float)endpoint_dot;
    if(!(endpoint_dot<0)) {
        if(thug_skater_orientation_context->identifier==0xd443a2bc)goto leave;
        thug_rail_point(p->rail_transform,start_point,selected);thug_rail_point(p->rail_transform,end_point,end);
        float rail[4],motion[4];thug_vector_difference(rail,end_point,start_point);thug_vector_difference(motion,to,from);
        float rail_length=(float)thug_vector_length(rail);
        if(thug_vector_length(motion)<rail_length)goto leave;
        if(stored_dot>=0) {
            thug_rail_point(p->rail_transform,start_point,selected);thug_rail_point(p->rail_transform,end_point,end);
            float sum[4];thug_vector_sum(sum,end_point,start_point);thug_vector_divided(point,sum,2);
        }
    }
    thug_rail_point(p->rail_transform,start_point,selected);thug_rail_point(p->rail_transform,end_point,end);
    float direction[4];thug_vector_difference(direction,end_point,start_point);thug_vector_normalize(direction);
    ThugSkaterBody *body=p->body;
    if(body->velocity[0]==0&&body->velocity[2]==0) {
        __builtin_memcpy(body->velocity,body->orientation+8,4);
        __builtin_memcpy(p->body->velocity+2,p->body->orientation+10,4);
    }
    body=p->body;float sign=(float)thug_sign_nonnegative((float)thug_vector_dot(direction,body->velocity));
    thug_vector_align_magnitude(body->velocity,direction);thug_vector_scale(p->body->velocity,sign);
    p->rail_node=selected;thug_vector_copy(p->body->position,point);
    const uint32_t change[3]={13,3,0};thug_skater_rail_event(p,change,d,m);
    thug_skater_set_material(p,(uint8_t)p->rail_node->unknown_50,d,m);return;
leave:;
    const uint32_t release[3]={13,4,0};thug_skater_rail_event(p,release,d,m);
    thug_skater_change_state(p,1,d,m);p->body->position[1]=(float)R((double)p->body->position[1]+1);
    thug_object_emit_event((void *)p->body,0xafaa46ba,0,d,m);
}
#undef R

#undef R

/* 0050ddf0: complete rail-state recovery. */
#include "rail.h"
#include "moving_contact.h"
#include "balance.h"
#include "objectives.h"
#include "nodes.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../script/delivery.h"
#include "../platform/math.h"
#define R thug_platform_round_x87_single
static void flag(void *base,unsigned off,uint8_t v) {
    uint8_t *p=(uint8_t *)base+off;
    if(*p!=v) {*p=v;uint32_t now=thug_elapsed_time()+thug_timer_offset;__builtin_memcpy(p+4,&now,4);}
}
static void points(ThugSkaterPhysics *p,ThugRailNode *a,ThugRailNode *b,float av[4],float bv[4]) {
    thug_rail_point(p->rail_transform,av,a);thug_rail_point(p->rail_transform,bv,b);
}
static void difference_wide(double out[4],const float a[4],const float b[4]) {
    for(unsigned i=0;i<4;++i)out[i]=R((double)a[i]-b[i]);
}
static double length_order(const double v[4],unsigned a,unsigned b,unsigned c) {
    return R(__builtin_sqrt(R(R(R(v[a]*v[a])+R(v[b]*v[b]))+R(v[c]*v[c]))));
}
static uint8_t clearance(ThugSkaterPhysics *p,ThugRailNode *a,ThugRailNode *b,ThugCollisionQuery *q) {
    float av[4],bv[4];points(p,b,a,bv,av);
    return thug_rail_clearance(av[0],av[1],av[2],av[3],bv[0],bv[1],bv[2],bv[3],q);
}
static void rail_basis(float basis[16]) {
    thug_vector_normalize(basis+8);
    __builtin_memcpy(basis,basis+10,4);basis[2]=-basis[8];basis[1]=basis[3]=0;
    thug_vector_normalize(basis);
    float up[4];thug_vector_cross(up,basis+8,basis);thug_vector_copy(basis+4,up);thug_vector_normalize(basis+4);
}
void thug_skater_update_rail(ThugSkaterPhysics *p,ThugCollisionQuery *q,const ThugDiagnostics *d,const ThugMemory *m) {
    flag(p->state,0x78,0);flag(p->state,0xa8,0);flag(p->state,0x80,0);flag(p->state,0xb0,0);
    p->ground_flag_2e4=0;ThugSkaterGroundGate *gate=p->ground_gate;
    if(gate->contact) {
        if(!gate->contact->reference.object)thug_skater_moving_contact_release(gate,m);
        else {
            ThugTransformComponent *component=(void *)thug_object_find_component((void *)gate->contact->reference.object,0x1cdfb2a3);
            float world[16];thug_component_world_transform(component,world);
            gate=p->ground_gate;
            if(gate->contact) {
                if(!gate->contact->reference.object||!thug_moving_contact_update(gate->contact,p->body->position))thug_skater_moving_contact_release(gate,m);
                else {
                    thug_vector_add(p->body->position,p->ground_gate->contact->displacement);
                    if(p->ground_gate->contact->orientation_changed) {
                        thug_matrix_multiply(p->body->orientation,p->body->orientation,p->ground_gate->contact->rotation);
                        thug_matrix_multiply(p->cached_orientation,p->cached_orientation,p->ground_gate->contact->rotation);
                    }
                }
            }
        }
    }
    ThugSkaterBody *parameter_body=p->body;
    p->rail_retry_delay=thug_truncate_low_word(thug_script_get_global_number(0x2b4645ad,1));
    flag(p->state,0x50,0);
    if(thug_skater_handle_input_release(p,d,m)) {
        const uint32_t first[3]={2,4,0},second[3]={13,4,0};
        thug_skater_rail_event(p,first,d,m);thug_skater_rail_event(p,second,d,m);
        p->rail_retry_delay=thug_truncate_low_word(thug_script_get_global_number(0x0bf35053,1));
        flag(p->state,0xd0,1);flag(p->state,0xd8,1);
        p->body->position[1]=(float)R((double)p->body->position[1]+1);goto finish;
    }
    if(p->mode_context->identifier==0x255ed86f||p->mode_context->identifier==0x8d10119d) {
        thug_balance_update((void *)((uint8_t *)p->mode_context+0x7c),d,m);
        if(thug_gameplay_flag(thug_game_context->gameplay_flags,0xcd09e062)) {
            ThugGameplayFlags *flags=thug_game_context->gameplay_flags;
            thug_gameplay_flag_set(flags,thug_script_get_global_integer(0xcd09e062,0));
            ((ThugBalance *)((uint8_t *)p->mode_context+0x7c))->position=0;
            ((ThugBalance *)((uint8_t *)p->mode_context+0x7c))->velocity=0;thug_last_gameplay_flag=1;
        }
    }
    ThugRailNode *original=p->rail_node,*end=original->next,*continuation=0;
    if(!end) {thug_skater_update_natas(p,q,d,m);return;}
    float av[4],bv[4],direction[4];double wide[4];
    points(p,original,end,av,bv);difference_wide(wide,bv,av);
    float segment_length=(float)length_order(wide,0,1,2);
    double inverse=R(1.0/segment_length);
    for(unsigned i=0;i<4;++i)direction[i]=(float)R(wide[i]*(i?(double)(float)inverse:inverse));
    float old_sign=thug_vector_dot(direction,p->body->velocity)<0?-1:1;
    float gravity[4]={0,(float)thug_skater_get_parameter(0xd1f46992,1,parameter_body),0,1};
    thug_vector_project_axis(gravity,direction);
    ThugSkaterBody *body=p->body;
    for(unsigned i=0;i<4;++i) {
        double product=R((double)p->time_step*gravity[i]);if(i)product=(float)product;
        body->velocity[i]=(float)R(product+body->velocity[i]);
    }
    float sign=thug_vector_dot(direction,p->body->velocity)<0?-1:1;
    if(sign!=old_sign)p->unknown_34c_to_34f[0]=!p->unknown_34c_to_34f[0];
    uint8_t needs_search=1;ThugRailNode *linked=sign>=0?end->next:original->previous;
    if(linked&&(linked->flags&4)) {
        float first[4],second[4];
        if(sign>=0) {
            points(p,end,original,av,bv);thug_vector_difference(first,bv,av);
            points(p,end->next,end,av,bv);thug_vector_difference(second,bv,av);
        } else {
            points(p,original,end,av,bv);thug_vector_difference(first,bv,av);
            points(p,original->previous,original,av,bv);thug_vector_difference(second,bv,av);
        }
        first[1]=second[1]=0;thug_vector_normalize(first);thug_vector_normalize(second);
        float dot=(float)thug_vector_dot(second,first);
        double threshold=thug_platform_cos(R(thug_script_get_global_number(0x76c1da15,1)*.01745329238474369f));
        if(!(threshold>dot)) {needs_search=0;continuation=sign>=0?end:original->previous;}
    }
    float excess=0;body=p->body;
    thug_rail_point(p->rail_transform,av,sign<0?end:original);
    difference_wide(wide,body->position,av);double distance=length_order(wide,2,1,0);
    if(distance>R((double)segment_length+.10000000149011612f)) {
        excess=(float)R(distance-segment_length);ThugRailNode *boundary=sign<0?original:end;
        uint8_t clear=0;
        if(sign<0) {
            if(original->previous&&(original->previous->flags&4))clear=clearance(p,original,original->previous,q);
        } else if(end->next&&(end->flags&4))clear=clearance(p,end,end->next,q);
        if(clear&&!needs_search) {
            thug_rail_point(p->rail_transform,av,boundary);thug_vector_copy(p->body->position,av);
            p->rail_node=sign<0?original->previous:end;
            thug_skater_set_material(p,(uint8_t)p->rail_node->unknown_50,d,m);
            const uint32_t change[3]={13,3,0};thug_skater_rail_event(p,change,d,m);
        } else {
            thug_rail_point(p->rail_transform,av,boundary);thug_skater_transition_rail(p,av,q,d,m);
        }
    }
    if(p->state->mode!=4)goto finish;
    ThugRailNode *current=p->rail_node,*current_end=current->next;
    points(p,current,current_end,av,bv);thug_vector_difference(direction,bv,av);thug_vector_normalize(direction);
    sign=thug_vector_dot(direction,p->body->velocity)<0?-1:1;
    p->rail_reentry_time=thug_elapsed_time()+thug_timer_offset;
    thug_vector_align_magnitude(p->body->velocity,direction);thug_vector_scale(p->body->velocity,sign);
    if(p->unknown_34c_to_34f[0])sign=-sign;
    float heading[4],blended[4];for(unsigned i=0;i<4;++i)heading[i]=(float)R((double)direction[i]*sign);
    thug_vector_lerp(blended,p->cached_orientation+8,heading,.30000001192092896f);
    thug_vector_copy(p->cached_orientation+8,blended);rail_basis(p->cached_orientation);
    thug_vector_copy(p->body->orientation+8,heading);rail_basis(p->body->orientation);
    points(p,current,current_end,av,bv);difference_wide(wide,bv,av);
    if(length_order(wide,0,2,1)<=excess)excess=0;
    float prior[4],delta[4],unit_delta[4];body=p->body;thug_vector_copy(prior,body->position);
    for(unsigned i=0;i<4;++i) {
        double product=R((double)p->time_step*body->velocity[i]);if(i)product=(float)product;
        body->position[i]=(float)R(product+body->position[i]);
    }
    body=p->body;
    for(unsigned i=0;i<4;++i) {
        double product=R((double)heading[i]*excess);if(i>=2)product=(float)product;
        body->position[i]=(float)R(product+body->position[i]);
    }
    p->body->position[3]=(float)R((double)p->body->position[3]+1);
    thug_vector_difference(delta,p->body->position,prior);thug_vector_copy(unit_delta,delta);thug_vector_normalize(unit_delta);
    if(!needs_search) {
        if(thug_skater_orientation_context->identifier==0xd443a2bc)goto finish;
        float first[4],second[4];points(p,original,original->next,av,bv);thug_vector_difference(first,bv,av);
        points(p,continuation,continuation->next,av,bv);thug_vector_difference(second,bv,av);
        thug_vector_normalize(first);thug_vector_normalize(second);
        if(!(__builtin_fabs(R((double)first[1]-second[1]))<.009999999776482582f))goto finish;
    }
    thug_vector_copy(p->surface_segment,prior);thug_vector_copy(p->surface_segment+4,p->body->position);
    for(unsigned i=0;i<4;++i) {
        double product=R((double)unit_delta[i]*6);if(i>=2)product=(float)product;
        double sum=R(product+delta[i]);if(i==0||i==3)sum=(float)sum;
        p->surface_segment[4+i]=(float)R(sum+p->surface_segment[4+i]);
    }
    thug_vector_add(p->surface_segment,p->body->orientation+4);thug_vector_add(p->surface_segment+4,p->body->orientation+4);
    if(thug_skater_query_surface(p,0x10,0,q)&&(thug_skater_orientation_context->identifier==0xd443a2bc||!(p->surface_probe.result.surface_flags&0x1000))) {
        const uint32_t leave[3]={13,4,0};thug_skater_rail_event(p,leave,d,m);
        thug_vector_copy(p->body->position,p->body->previous_position);
        p->body->position[1]=(float)R((double)p->body->position[1]+1);
        thug_vector_project_plane(p->body->velocity,p->surface_probe.normal);
        thug_skater_change_state(p,1,d,m);thug_object_emit_event((void *)p->body,0xafaa46ba,0,d,m);
    }
finish:
    thug_vector_copy(p->orientation_target,p->body->orientation+4);
    int32_t score_delta;__builtin_memcpy(&score_delta,(uint8_t *)p+0x3a8,4);
    ThugScore *score=p->score_component->score;
    thug_score_add_balance(score,thug_truncate_low_word(R((double)score_delta*score->multiplier_154c)),d,m);
    if(p->rail_transform->unknown_44) {
        ThugScriptStructure *node=thug_node_find(p->rail_node->name,1);
        thug_script_get_checksum_legacy(node,0xa1dc81f9,&p->rail_name,1);thug_skater_notify(p->name_context,p->rail_name,d,m);
    }
}
#undef R

#undef R
