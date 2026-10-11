#include "skater.h"
#include "../core/vector.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include <stddef.h>
_Static_assert(offsetof(ThugSkaterWallGate, movement_mode)==0x2c,"Movement mode pointer");
_Static_assert(offsetof(ThugSkaterMovementMode, alternate)==0x118,"Alternate movement mode");
_Static_assert(offsetof(ThugSkaterTransferMotion, direction)==0x48,"Transfer direction");
_Static_assert(offsetof(ThugSkaterTransferMotion, speed_factor)==0x1868,"Transfer speed factor");
_Static_assert(offsetof(ThugSkaterPhysics, transfer_motion)==0x1534,"Transfer component");
_Static_assert(offsetof(ThugSkaterState, skip_ground_probe_time)==0x7c,"Probe flag time");
_Static_assert(offsetof(ThugSkaterTransferResult, moving)==0x24,"Transfer output");
static double r24(double x) { return thug_platform_round_x87_single(x); }
static int transfer_mode(const ThugSkaterPhysics *p) {
    return !p->wall_gate->movement_mode->alternate && p->wall_gate->movement_mode->mode==1;
}
static void probe_flag(ThugSkaterPhysics *p,uint8_t value) {
    ThugSkaterState *state=p->state;
    if (state->skip_ground_probe!=value) {
        state->skip_ground_probe=value;
        state->skip_ground_probe_time=thug_elapsed_time()+thug_timer_offset;
    }
}
/* Inlined twice in 502240. The height delta spills before gravity is read;
 * the discriminant doubles its product before adding the velocity square. */
static double flight_time(ThugSkaterPhysics *p,const float from[4],const float velocity[4],float y) {
    probe_flag(p,1);
    float delta=(float)r24((double)from[1]-y),vy=velocity[1];
    double gravity=-thug_skater_gravity(p),product=r24(delta*gravity);
    double discriminant=r24(r24(product+product)+r24((double)vy*vy));
    return discriminant<0 ? (double)0.00001f : r24(r24(r24(__builtin_sqrt(discriminant))+vy)/gravity);
}
/* 0x0043daa0. Both required numeric members are fetched through the original
 * global-structure lookup; the final interpolation retains the x87 exponent. */
double thug_skater_transfer_speed(const ThugSkaterTransferMotion *motion) {
    float high,low;
    thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0x7213ef07,&high,1);
    thug_script_get_float(thug_script_get_global_structure(0x6775e538,0),0xcc461b87,&low,1);
    return r24(r24(r24((double)high-low)*motion->speed_factor)+low);
}
/* 0x00502240. Complete forward scan and two-segment ballistic clearance test.
 * All candidates and clearance probes use the original collision pipeline.
 * The automatic cache registers/unregisters with the eight-slot registry. */
uint8_t thug_skater_find_transfer(ThugSkaterPhysics *p,uint8_t force_vertical,
        const float from[4],const float scan_origin[4],float velocity[4],
        ThugSkaterTransferResult *out,ThugCollisionQuery *query) {
    float direction[4],origin[4];
    ThugSkaterMovementMode *mode=p->wall_gate->movement_mode;
    if (!mode->alternate && !mode->mode) {
        double length=r24(__builtin_sqrt(r24(r24((double)velocity[0]*velocity[0])+r24((double)velocity[2]*velocity[2]))));
        if (length<(double)0.01f) return 0;
        double inverse=r24(1/length);
        direction[0]=(float)r24(inverse*velocity[0]); direction[1]=(float)r24(0.0*inverse);
        direction[2]=(float)r24(inverse*velocity[2]); direction[3]=(float)r24(inverse*velocity[3]);
    } else thug_vector_copy(direction,p->transfer_motion->direction);
    thug_vector_copy(origin,scan_origin);
    if (from[1]>origin[1]) origin[1]=from[1];
    float maximum=500,offset=0;
    if (transfer_mode(p)) {
        if (!p->transfer_motion->mode) { maximum=(float)thug_script_get_global_number(0xe50a9d56,0); offset=200; }
        else for (unsigned i=0;i<4;++i) origin[i]=(float)r24(origin[i]-r24((double)direction[i]*12));
    }
    ThugCollisionProbe probe; thug_collision_probe_initialize(&probe);
    ThugCollisionCache cache; thug_collision_cache_initialize(&cache);
    ThugBounds bounds; thug_bounds_reset(&bounds);
    float point[4]; thug_vector_copy(point,origin);
    point[1]=(float)r24((double)point[1]+offset); thug_bounds_expand(&bounds,point);
    point[1]=(float)r24((double)point[1]-4200); thug_bounds_expand(&bounds,point);
    for (unsigned i=0;i<4;++i) {
        double product=r24((double)direction[i]*maximum);
        point[i]=(float)r24(origin[i]+(i==3?product:(float)product));
    }
    point[1]=(float)r24((double)point[1]+offset); thug_bounds_expand(&bounds,point);
    point[1]=(float)r24((double)point[1]-4200); thug_bounds_expand(&bounds,point);
    thug_collision_cache_build(&cache,&bounds); probe.cache=&cache;
    float distance=0.01f,normal[4],saved_velocity[4];
    double next=distance;
    while (next<maximum) {
        for (unsigned i=0;i<4;++i) {
            double product=r24((double)direction[i]*distance);
            probe.segment[i]=probe.segment[i+4]=(float)r24(origin[i]+(i==3?product:(float)product));
        }
        float y=probe.segment[1];
        probe.segment[1]=(float)r24((double)y+offset); probe.segment[5]=(float)r24((double)y-4000);
        if (thug_collision_probe_query(&probe,1,0,query) && (probe.result.surface_flags&8)
                && __builtin_fabsf(probe.normal[1])<(double)0.707f) {
            float horizontal[4]; thug_vector_copy(horizontal,probe.normal); horizontal[1]=0;
            thug_vector_copy(normal,probe.normal); thug_vector_normalize(horizontal);
            double dot=r24(r24(r24((double)horizontal[2]*direction[2])+r24((double)horizontal[1]*direction[1]))+r24((double)horizontal[0]*direction[0]));
            if (dot>=(double)0.05f || (transfer_mode(p) && p->transfer_motion->mode==1 && dot<=-0.25)) goto contact;
        }
        next=distance;
        if (next>100) next=r24(next+24);
        next=r24(next+3); distance=(float)next;
    }
    goto failed;
contact:
    thug_vector_copy(origin,probe.point);
    uint8_t moving=thug_collision_probe_has_moving_object(&probe);
    float original_height=origin[1];
    double dw=r24((double)origin[3]-from[3]);
    float dz=(float)r24((double)origin[2]-from[2]);
    double wide_dx=r24((double)origin[0]-from[0]); float dx=(float)wide_dx;
    distance=(float)r24(__builtin_sqrt(r24(r24(wide_dx*dx)+r24((double)dz*dz))));
    double dot=r24(r24(r24((double)direction[2]*dz)+r24((double)dx*direction[0]))+r24((double)direction[1]*0.0));
    if (dot<0) distance=-distance;
    thug_vector_copy(saved_velocity,velocity);
    double inverse=r24(1.0/distance); float stored_inverse=(float)inverse;
    direction[0]=(float)r24((double)stored_inverse*dx); direction[1]=(float)r24((double)stored_inverse*0.0);
    direction[2]=(float)r24((double)stored_inverse*dz); direction[3]=(float)r24(inverse*dw);
    if (transfer_mode(p)) { thug_vector_project_axis(velocity,direction); velocity[1]=saved_velocity[1]; }
    float speed=(float)r24(__builtin_sqrt(r24(r24((double)velocity[2]*velocity[2])+r24((double)velocity[0]*velocity[0]))));
    if (transfer_mode(p)) {
        float minimum=(float)thug_skater_transfer_speed(p->transfer_motion);
        if (speed<minimum) {
            ThugSkaterTransferMotion *motion=(ThugSkaterTransferMotion *)thug_object_find_component(p->body,0x726e85aa);
            velocity[0]=(float)r24((double)minimum*motion->direction[0]);
            motion=(ThugSkaterTransferMotion *)thug_object_find_component(p->body,0x726e85aa);
            velocity[2]=(float)r24((double)minimum*motion->direction[2]); speed=minimum;
        }
    }
    ThugSkaterBody *body=p->body;
    if (force_vertical) {
        double minimum=thug_skater_get_parameter(0x95a79c32,1,body);
        velocity[1]=(float)(velocity[1]>minimum?velocity[1]:minimum);
    }
    if (!(transfer_mode(p) && !p->transfer_motion->mode)) {
        double maximum_y=thug_skater_get_parameter(0x95a79c32,1,body); maximum_y=r24(maximum_y+maximum_y);
        velocity[1]=(float)(velocity[1]<maximum_y?velocity[1]:maximum_y);
    }
    probe_flag(p,1); float gravity=(float)thug_skater_gravity(p); probe_flag(p,0);
    float predicted=from[1];
    if (distance>0 && speed>(double)0.0001f) {
        double t=r24((double)distance/speed);
        predicted=(float)r24(r24(r24(r24(r24(gravity*t)*0.5)+velocity[1])*t)+from[1]);
    }
    if (transfer_mode(p) && velocity[1]>0 && from[1]<origin[1]
            && r24(__builtin_fabs((double)distance)/speed)<-r24((double)velocity[1]/gravity))
        predicted=(float)r24(r24(r24((double)velocity[1]*velocity[1])/r24((double)gravity*-2))+from[1]);
    if (predicted<origin[1]) goto restore;
    float flight=(float)flight_time(p,from,velocity,origin[1]); probe_flag(p,0);
    if (thug_script_get_global_number(0x32c20f7e,0)>flight) goto restore;
    if (!(origin[1]<predicted)) goto restore;
    float half_distance=(float)r24((double)distance*0.5);
    do {
        thug_vector_copy(probe.segment,from);
        float t=(float)r24(flight_time(p,from,velocity,origin[1])*0.5); probe_flag(p,0);
        double horizontal=r24(r24((double)half_distance/t)*t);
        float midpoint=(float)r24(r24(r24(r24(r24((double)t*t)*gravity)*0.5)+r24((double)t*velocity[1]))+from[1]);
        for (unsigned i=0;i<4;++i) {
            double product=r24(direction[i]*horizontal);
            probe.segment[i+4]=(float)r24((i==1?midpoint:from[i])+(i==0?product:(float)product));
        }
        if (!thug_collision_probe_query(&probe,1,0,query)) {
            thug_vector_copy(probe.segment,probe.segment+4); thug_vector_copy(probe.segment+4,origin);
            probe.segment[5]=(float)r24((double)origin[1]+1);
            if (!thug_collision_probe_query(&probe,1,0,query)) {
                thug_vector_copy(out->position,origin); thug_vector_copy(out->normal,normal);
                out->moving=moving; out->original_height=original_height;
                thug_collision_cache_destroy(&cache); thug_collision_probe_release(&probe); return 1;
            }
        }
        next=r24((double)origin[1]+24); origin[1]=(float)next;
    } while (next<predicted);
restore:
    thug_vector_copy(velocity,saved_velocity);
failed:
    thug_collision_cache_destroy(&cache); thug_collision_probe_release(&probe); return 0;
}

#include "../script/schedule.h"
#include "../script/values.h"
#include "../script/events.h"
_Static_assert(offsetof(ThugSkaterState,transfer_flag_a8)==0xa8,"Transfer state flag");
_Static_assert(offsetof(ThugSkaterState,transfer_velocity)==0xe4,"Transfer state velocity");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_height)==0x37c,"Transfer height");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_surface)==0x3b0,"Transfer surface basis");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_interpolation)==0x3f0,"Transfer interpolation");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_progress)==0x488,"Transfer progress");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_direction)==0x490,"Transfer direction");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_previous_orientation)==0x4a0,"Previous transfer basis");
_Static_assert(offsetof(ThugSkaterPhysics,transfer_moving)==0x14c0,"Transfer moving flag");
float thug_skater_transfer_velocity[4]; /* 0x007ccdbc */
static void set_timed_flag(uint8_t *flag,uint32_t *time,uint8_t value) {
    if (*flag!=value) { *flag=value; *time=thug_elapsed_time()+thug_timer_offset; }
}
/* 0x00502f20. Apply the complete transfer, construct its orientation transition,
 * spawn the real transfer script with height parameters, then remove the old
 * input-release handler. Script callbacks may replace body/state pointers. */
void thug_skater_apply_transfer(ThugSkaterPhysics *p,const ThugSkaterTransferResult *contact,
        const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    ThugSkaterBody *body=p->body;
    double dw=r24((double)contact->position[3]-body->position[3]);
    float dz=(float)r24((double)contact->position[2]-body->position[2]);
    double wide_dx=r24((double)contact->position[0]-body->position[0]); float dx=(float)wide_dx;
    float distance=(float)r24(__builtin_sqrt(r24(r24(wide_dx*dx)+r24((double)dz*dz))));
    double dot=r24(r24(r24((double)dz*body->velocity[2])+r24((double)dx*body->velocity[0]))+r24((double)body->velocity[1]*0.0));
    if (dot<0) distance=-distance;
    double inverse=r24(1.0/distance); float stored_inverse=(float)inverse;
    float direction[4]={(float)r24((double)stored_inverse*dx),(float)r24((double)stored_inverse*0.0),
        (float)r24((double)stored_inverse*dz),(float)r24(inverse*dw)};
    float flight=(float)flight_time(p,p->body->position,p->body->velocity,contact->position[1]);
    float speed=(float)r24((double)distance/flight); probe_flag(p,0);
    ThugSkaterState *state=p->state;
    state->transfer_velocity[1]=0; state->transfer_velocity[3]=1;
    state->transfer_velocity[0]=(float)r24((double)direction[0]*speed);
    state->transfer_velocity[2]=(float)r24((double)direction[2]*speed);
    thug_vector_copy(thug_skater_transfer_velocity,p->state->transfer_velocity);
    state=p->state; p->transfer_height=contact->position[1];
    set_timed_flag(&state->skip_ground_probe,&state->skip_ground_probe_time,1);
    state=p->state; set_timed_flag(&state->ground_transition_flag,&state->ground_transition_time,1);
    state=p->state; set_timed_flag(&state->transfer_flag_a8,&state->transfer_time_ac,1);
    state=p->state; set_timed_flag(&state->transition_flag_38,&state->transition_time_3c,0);
    state=p->state; set_timed_flag(&state->transition_flag_68,&state->transition_time_6c,0);
    p->transfer_moving=contact->moving;
    p->body->velocity[0]=0; p->body->velocity[2]=0;
    float previous[16]; thug_matrix_copy(previous,p->body->orientation);
    const float *normal=contact->normal;
    double slope_y=-r24(r24(r24((double)direction[0]*normal[0])+r24((double)direction[2]*normal[2]))/normal[1]);
    double length=r24(__builtin_sqrt(r24(r24(r24((double)direction[0]*direction[0])+r24(slope_y*slope_y))+r24((double)direction[2]*direction[2]))));
    float surface_direction[4]={direction[0],0,direction[2],direction[3]};
    if (length>0) {
        double scale=r24(1/length);
        surface_direction[0]=(float)r24((double)direction[0]*scale);
        slope_y=r24(slope_y*scale); surface_direction[2]=(float)r24((double)direction[2]*scale);
    }
    surface_direction[1]=(float)slope_y;
    thug_vector_project_plane(surface_direction,normal); thug_vector_normalize(surface_direction);
    float target[16]; thug_vector_copy(target+4,normal);
    thug_vector_copy(p->transfer_direction,surface_direction);
    target[2]=(float)r24(r24((double)target[4]*surface_direction[1])-r24((double)target[5]*surface_direction[0]));
    target[1]=(float)r24(r24((double)target[6]*surface_direction[0])-r24((double)target[4]*surface_direction[2]));
    target[0]=(float)r24(r24((double)target[5]*surface_direction[2])-r24((double)target[6]*surface_direction[1]));
    target[3]=0; thug_vector_copy(target+8,surface_direction);
    target[12]=target[13]=target[14]=0; target[15]=1;
    thug_matrix_copy(p->transfer_surface,target);
    if (p->transfer_surface[9]>0) {
        for (unsigned i=8;i<12;++i) p->transfer_surface[i]=(float)r24((double)p->transfer_surface[i]*-1);
        for (unsigned i=0;i<4;++i) p->transfer_surface[i]=(float)r24((double)p->transfer_surface[i]*-1);
    }
    float forward[4]; thug_vector_copy(forward,p->body->orientation+8); forward[1]=0;
    float angle=(float)-thug_vector_signed_angle(forward,direction,p->body->orientation+4);
    float yaw[16]; thug_matrix_rotation_y(yaw,angle); thug_matrix_multiply(target,yaw,target);
    thug_matrix_interpolation_initialize(&p->transfer_interpolation,previous,target);
    p->transfer_progress=0; p->transfer_duration=flight;
    thug_matrix_copy(p->transfer_previous_orientation,previous);
    /* The pre-existing host allocator boundary replaces original heap startup. */
    ThugScriptStructure *parameters=thug_script_structure_allocate(8,memory);
    if (parameters) thug_script_structure_initialize(parameters);
    union { float value; uint32_t bits; } height={.value=(float)r24((double)p->body->position[1]-contact->original_height)};
    thug_script_set_float_bits(parameters,0xbb00fe40,height.bits,memory);
    thug_object_spawn_script((ThugReferencedObject *)p->body,0xc7ed5fef,UINT32_MAX,0,0,parameters,diagnostics,memory);
    if (parameters) { thug_script_structure_destroy(parameters,memory); thug_script_structure_free(parameters,memory); }
    state=p->state; set_timed_flag(&state->transfer_flag_b0,&state->transfer_time_b4,1);
    thug_object_remove_event((ThugReferencedObject *)p->body,0x8ffefb28,memory);
}

/* 0x004fee10. Complete alternate-contact scan; failed searches retain outputs. */
uint8_t thug_skater_find_alternate_transfer(ThugSkaterPhysics *p,const float direction[4],const float normal[4],
        uint8_t *opposed,float point[4],float contact_normal[4],uint8_t *moving,ThugCollisionQuery *query) {
    ThugCollisionProbe probe; thug_collision_probe_initialize(&probe);
    ThugCollisionCache cache; thug_collision_cache_initialize(&cache);
    ThugBounds bounds; thug_bounds_reset(&bounds);
    float corner[4];
    for (unsigned end=0;end<2;++end) {
        for (unsigned i=0;i<4;++i) {
            double product=r24((double)direction[i]*(end?500:10));
            corner[i]=(float)r24(p->body->position[i]+(i==3?product:(float)product));
        }
        thug_bounds_expand(&bounds,corner); corner[1]=(float)r24((double)corner[1]-4000); thug_bounds_expand(&bounds,corner);
    }
    thug_collision_cache_build(&cache,&bounds); probe.cache=&cache;
    float distance=10; double next;
    do {
        for (unsigned i=0;i<4;++i) {
            double product=r24((double)direction[i]*distance);
            probe.segment[i]=probe.segment[i+4]=(float)r24(p->body->position[i]+(i==3?product:(float)product));
        }
        float y=probe.segment[1]; probe.segment[1]=(float)r24((double)y+400); probe.segment[5]=(float)r24((double)y-4000);
        if (thug_collision_probe_query(&probe,1,0,query) && (probe.result.surface_flags&8)
                && __builtin_fabsf(probe.normal[1])<(double)0.707f) {
            float horizontal[4]; thug_vector_copy(horizontal,probe.normal); horizontal[1]=0; thug_vector_normalize(horizontal);
            double dot=r24(r24(r24((double)horizontal[2]*normal[2])+r24((double)horizontal[1]*normal[1]))+r24((double)horizontal[0]*normal[0]));
            if (dot<=(double)0.95f) {
                float saved_dot=(float)dot;
                thug_vector_copy(point,probe.point); thug_vector_copy(contact_normal,probe.normal);
                *moving=thug_collision_probe_has_moving_object(&probe); *opposed=saved_dot>(double)-0.866f;
                thug_collision_cache_destroy(&cache); thug_collision_probe_release(&probe); return 1;
            }
        }
        next=r24((double)distance+6); distance=(float)next;
    } while (next<500);
    thug_collision_cache_destroy(&cache); thug_collision_probe_release(&probe); return 0;
}

/* 0x00505f70. Test and apply an alternate transition, including the original
 * deferred/blocked result and complete interpolation/script/event effects. */
uint8_t thug_skater_try_alternate_transfer(ThugSkaterPhysics *p,ThugCollisionQuery *query,
        const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    ThugSkaterBody *body=p->body;
    float up[4]={body->orientation[4],0,body->orientation[6],0};
    double length=r24(__builtin_sqrt(r24(r24((double)up[0]*up[0])+r24((double)up[2]*up[2]))));
    if (length>0) { double scale=r24(1/length); for (unsigned i=0;i<3;++i) up[i]=(float)r24((double)up[i]*scale); }
    float axis[4]={-up[2],0,up[0],0},direction[4]; thug_vector_negated(direction,body->velocity);
    length=thug_vector_length(direction);
    if (length>0) { double scale=r24(1/length); for (unsigned i=0;i<3;++i) direction[i]=(float)r24((double)direction[i]*scale); }
    float rotation[4],target[4]; thug_quaternion_axis_angle(rotation,axis,1.5707963705062866f);
    thug_quaternion_rotate(rotation,target,direction);
    ThugCollisionProbe probe; thug_collision_probe_initialize(&probe);
    for (unsigned i=0;i<4;++i) probe.segment[i]=probe.segment[i+4]=(float)r24((double)(float)r24((double)target[i]*0.5)+p->body->position[i]);
    probe.segment[5]=(float)r24((double)probe.segment[5]-4000);
    uint8_t opposed=0,moving=0;
    if (!thug_collision_probe_query(&probe,1,0,query)) goto failed_alternate;
    float first_x=probe.point[0],first_z=probe.point[2],horizontal[4],contact_normal[4],back[4];
    thug_vector_copy(horizontal,probe.normal); horizontal[1]=0; thug_vector_normalize(horizontal);
    thug_vector_negated(back,target);
    if (!thug_skater_find_alternate_transfer(p,back,horizontal,&opposed,target,contact_normal,&moving,query)) {
        float side[4]; uint8_t left=p->input->button_60.pressed,right=p->input->button_80.pressed;
        if (left && !right) { float normal_left[4]={-horizontal[2],0,horizontal[0],1}; thug_vector_sum(side,back,normal_left); }
        else if (!left && right) { float normal_right[4]={horizontal[2],0,-horizontal[0],-1}; thug_vector_sum(side,normal_right,back); }
        else goto failed_alternate;
        thug_vector_normalize(side);
        if (!thug_skater_find_alternate_transfer(p,side,horizontal,&opposed,target,contact_normal,&moving,query)) goto failed_alternate;
    }
    body=p->body; target[1]=body->position[1];
    double dx=r24((double)target[0]-first_x),dz=r24((double)target[2]-first_z);
    float distance=(float)r24(__builtin_sqrt(r24(r24(dx*dx)+r24(dz*dz))));
    thug_vector_copy(horizontal,contact_normal); horizontal[1]=0; thug_vector_normalize(horizontal);
    float saved_velocity[4]; thug_vector_copy(saved_velocity,body->velocity);
    double dot=r24(r24(r24((double)horizontal[2]*up[2])+r24((double)horizontal[1]*up[1]))+r24((double)horizontal[0]*up[0]));
    if (__builtin_fabs(dot)<(double)0.9f || distance>24) {
        body->velocity[1]=(float)thug_vector_length(body->velocity);
        p->body->velocity[0]=0; p->body->velocity[2]=0;
    }
    distance=(float)r24((double)distance+1);
    float time=(float)flight_time(p,p->body->position,p->body->velocity,target[1]); probe_flag(p,0);
    if (time<(double)0.1f) time=0.1f;
    double inverse=r24(1.0/time),speed=r24(inverse*distance); float inverse_stored=(float)inverse;
    if (distance>24 && thug_vector_length_squared(p->body->velocity)<r24(speed*speed)) goto failed_alternate;
    thug_vector_copy(probe.segment,p->body->position); thug_vector_copy(probe.segment+4,target); probe.segment[5]=p->body->position[1];
    if (thug_collision_probe_query(&probe,1,0,query)) { p->ground_transition_flag=1; thug_collision_probe_release(&probe); return 1; }
    p->ground_transition_flag=0; body=p->body;
    double dw=r24((double)target[3]-body->position[3]); dz=r24((double)target[2]-body->position[2]); dx=r24((double)target[0]-body->position[0]);
    direction[0]=(float)dx; direction[2]=(float)dz; direction[3]=(float)dw;
    if (!opposed) {
        direction[1]=(float)r24(r24(-1.0/contact_normal[1])*r24(r24((double)contact_normal[2]*dz)+r24((double)contact_normal[0]*dx)));
        thug_vector_normalize(direction);
    } else {
        direction[1]=(float)r24((double)target[1]-body->position[1]); thug_vector_normalize(direction);
        dot=r24(r24(r24((double)direction[2]*horizontal[2])+r24((double)direction[1]*horizontal[1]))+r24((double)direction[0]*horizontal[0]));
        direction[0]=direction[2]=0; direction[1]=dot<0?1:-1; direction[3]=1;
    }
    float previous[16],basis[16]; thug_matrix_copy(previous,body->orientation);
    thug_vector_copy(basis+8,direction); thug_vector_project_plane(basis+8,contact_normal); thug_vector_normalize(basis+8);
    thug_vector_copy(basis+4,contact_normal); thug_vector_cross(basis,basis+4,basis+8);
    thug_vector_copy(p->transfer_direction,basis+8); basis[12]=basis[13]=basis[14]=0; basis[15]=1;
    double angle=thug_vector_signed_angle(p->body->orientation+8,saved_velocity,p->body->orientation+4);
    if (__builtin_fabs(angle)<(double)0.5235987901687622f) angle=0;
    float yaw[16]; thug_matrix_rotation_y(yaw,(float)-angle); thug_matrix_multiply(basis,yaw,basis);
    thug_matrix_interpolation_initialize(&p->transfer_interpolation,previous,basis);
    p->transfer_progress=0; p->transfer_duration=time<(double)0.9f?0.9f:time;
    thug_matrix_copy(p->transfer_previous_orientation,previous);
    float halfway[16]; thug_matrix_interpolate(&p->transfer_interpolation,halfway,0.5f);
    if (halfway[5]<0) thug_matrix_interpolation_reverse(&p->transfer_interpolation);
    body=p->body; p->transfer_height=target[1];
    dw=r24((double)target[3]-body->position[3]);
    float delta[3]; for (unsigned i=0;i<3;++i) delta[i]=(float)r24((double)target[i]-body->position[i]);
    ThugSkaterState *state=p->state;
    for (unsigned i=0;i<3;++i) state->transfer_velocity[i]=(float)r24((double)inverse_stored*delta[i]);
    state->transfer_velocity[3]=(float)r24(dw*inverse_stored); p->state->transfer_velocity[1]=0;
    thug_object_spawn_script((ThugReferencedObject *)p->body,opposed?0x283bb5d6:0xa5179e9e,0,0,0,0,diagnostics,memory);
    thug_object_remove_event((ThugReferencedObject *)p->body,0x8ffefb28,memory);
    probe_flag(p,1);
    state=p->state; set_timed_flag(&state->transfer_flag_a8,&state->transfer_time_ac,0);
    state=p->state; set_timed_flag(&state->transition_flag_38,&state->transition_time_3c,0);
    state=p->state; set_timed_flag(&state->transition_flag_48,&state->transition_time_4c,0);
    p->transfer_moving=moving; thug_collision_probe_release(&probe); return 1;
failed_alternate:
    thug_collision_probe_release(&probe); return 0;
}

/* 0x00507120. Complete transition exit. A failed alternate search intentionally
 * returns after repairing the live orientation without refreshing its cache. */
void thug_skater_leave_transition(ThugSkaterPhysics *p,uint8_t force,ThugCollisionQuery *query,
        const ThugDiagnostics *diagnostics,const ThugMemory *memory) {
    ThugSkaterBody *saved_body=p->body; ThugSkaterInput *input=p->input;
    uint8_t trigger=0;
    if (input->button_20.pressed) {
        int32_t delay=(int32_t)thug_skater_get_integer_parameter(0x9d2f8cc8,1,saved_body);
        trigger=(int32_t)thug_input_button_elapsed(&input->button_20)>delay && !input->button_60.pressed
            && !input->button_80.pressed && !input->button_180.pressed && !input->button_160.pressed;
    }
    if (!trigger && !(input->button_c0.pressed && input->button_120.pressed) && !p->ground_transition_flag && !force) return;
    uint8_t alternate=(input->button_c0.pressed && input->button_120.pressed)||p->ground_transition_flag;
    if (alternate && thug_skater_try_alternate_transfer(p,query,diagnostics,memory)) {
        thug_matrix_copy(p->cached_orientation,p->body->orientation); return;
    }
    double amount;
    if (alternate) amount=24;
    else {
        float squared=(float)thug_vector_length_squared(p->body->velocity);
        double factor=thug_skater_get_parameter(0x13f33b41,1,saved_body);
        amount=r24(r24(__builtin_sqrt(squared))*factor);
    }
    p->body->velocity[0]=(float)r24(p->body->velocity[0]-r24(amount*p->orientation_source[0]));
    p->body->velocity[2]=(float)r24(p->body->velocity[2]-r24(amount*p->orientation_source[2]));
    if (!alternate) {
        float *vertical=p->body->velocity+1;
        double factor=thug_skater_get_parameter(0x848c5cd6,1,saved_body); *vertical=(float)r24(factor*(*vertical));
    }
    float angle=(float)r24(thug_skater_get_parameter(0xd757f4bb,1,saved_body)*(double)0.01745329238474369f);
    float rotation[16]; thug_matrix_rotation_x(rotation,angle); float *orientation=p->body->orientation;
    thug_matrix_multiply(orientation,rotation,orientation);
    ThugSkaterState *state=p->state; set_timed_flag(&state->ground_transition_flag,&state->ground_transition_time,0);
    state=p->state; set_timed_flag(&state->transition_flag_38,&state->transition_time_3c,0);
    state=p->state; set_timed_flag(&state->transition_flag_48,&state->transition_time_4c,0);
    state=p->state;
    if (alternate) set_timed_flag(&state->ground_contact_flag,&state->ground_contact_time,1);
    else set_timed_flag(&state->transfer_flag_b0,&state->transfer_time_b4,0);
    float direction[4]; thug_vector_copy(direction,p->body->velocity); thug_vector_normalize(direction);
    p->body->orientation[8]=direction[0]; p->body->orientation[10]=direction[2];
    thug_vector_normalize(p->body->orientation+8); thug_matrix_orthogonalize(p->body->orientation,2);
    if (!alternate) thug_matrix_copy(p->cached_orientation,p->body->orientation);
}
