#include "skater.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../core/matrix.h"
#include "../core/number.h"
#include "../platform/math.h"
#include <stddef.h>

_Static_assert(offsetof(ThugSkaterPhysics, repulsion_direction) == 0x2ac, "Repulsion direction");
_Static_assert(offsetof(ThugSkaterPhysics, repulsion_fraction) == 0x2bc, "Repulsion fraction");
_Static_assert(offsetof(ThugSkaterPhysics, repulsion_distance) == 0x2c0, "Repulsion distance");
_Static_assert(offsetof(ThugSkaterPhysics, repulsion_turn_rate) == 0x2c8, "Repulsion turn rate");
_Static_assert(offsetof(ThugSkaterPhysics, repulsion_times) == 0x328, "Repulsion timestamps");
#define R24 thug_platform_round_x87_single

/* 0x00501c90. The original loop reads the *opposite direction's* timestamp
 * three times, not each loop index's timestamp. Keep its repeated timer reads,
 * unsigned wrap and inclusive 500-unit window. Start/end copies are sequential. */
void thug_skater_repulsion_probe(ThugSkaterPhysics *p, const float start[4], const float end[4], uint32_t direction,
    ThugCollisionQuery *query) {
    for (uint32_t i = 0; i < 4; ++i) if (i != direction) {
        uint32_t previous = p->repulsion_times[direction ^ 1];
        if (thug_elapsed_time() + (thug_timer_offset - previous) > 500) return;
    }
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i] = start[i];
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i+4] = end[i];
    if (thug_skater_query_surface(p,0x10,0,query)) {
        for (unsigned i = 0; i < 4; ++i) p->repulsion_direction[i] += p->surface_probe.normal[i];
        if (p->surface_probe.fraction < p->repulsion_fraction) p->repulsion_fraction = p->surface_probe.fraction;
        p->repulsion_times[direction] = thug_elapsed_time() + thug_timer_offset;
    }
}

/* 0x005055b0. Four lateral/forward probes accumulate a repulsion vector.
 * Apply it at a depth-dependent magnitude, restore tangent velocity, then turn
 * away from the most recently retained surface normal when facing into it. */
void thug_skater_apply_repulsion(ThugSkaterPhysics *p, ThugCollisionQuery *query) {
    if (p->repulsion_distance == 0 || p->repulsion_strength == 0) return;
    p->repulsion_direction[0] = p->repulsion_direction[1] = p->repulsion_direction[2] = 0;
    p->repulsion_direction[3] = 1; p->repulsion_fraction = 1;
    const ThugSkaterBody *source = p->body;
    double height = thug_script_get_global_number(0xb45b39e2,1);
    double lifted_x = thug_platform_multiply_x87_single(height,source->orientation[4]);
    float lifted[3];
    for (unsigned i = 0; i < 3; ++i) lifted[i] = (float)thug_platform_multiply_x87_single(height,source->orientation[i+5]);
    float center[4];
    center[0] = (float)R24(lifted_x + p->body->position[0]);
    for (unsigned i = 1; i < 4; ++i) center[i] = lifted[i-1] + p->body->position[i];
    for (uint32_t direction = 0; direction < 4; ++direction) {
        const float *axis = p->body->orientation + (direction < 2 ? 0 : 8);
        float distance = p->repulsion_distance, delta[3], end[4];
        for (unsigned i = 0; i < 3; ++i) delta[i] = (float)R24((double)distance*axis[i]);
        double w = R24((double)distance*axis[3]);
        for (unsigned i = 0; i < 3; ++i) end[i] = direction & 1 ? center[i]-delta[i] : delta[i]+center[i];
        end[3] = (float)R24(direction & 1 ? (double)center[3]-w : w+center[3]);
        thug_skater_repulsion_probe(p,center,end,direction,query);
    }
    if (p->repulsion_fraction == 1) return;
    float magnitude = (float)R24(R24(1-(double)p->repulsion_fraction)*p->repulsion_strength);
    thug_vector_set_length(p->repulsion_direction,magnitude);
    for (unsigned i = 0; i < 4; ++i) p->body->velocity[i] += p->repulsion_direction[i];
    thug_vector_project_preserve_length(p->body->velocity,p->orientation_target);
    const float *normal = p->surface_probe.normal, *forward = p->body->orientation+8;
    double dot = R24(R24(R24((double)forward[2]*normal[2]) + R24((double)forward[1]*normal[1])) + R24((double)forward[0]*normal[0]));
    if (!(dot < 0)) return;
    float tangent[4];
    for (unsigned i = 0; i < 4; ++i) tangent[i] = forward[i];
    thug_vector_project_preserve_length(tangent,normal);
    float angle = (float)thug_vector_signed_angle(p->body->orientation+8,tangent,p->body->orientation+4);
    double step = R24(R24(thug_sign_nonnegative(angle)*p->repulsion_turn_rate)*p->time_step);
    float turn = (float)step;
    if (__builtin_fabsf(angle) < __builtin_fabs(step)) turn = angle;
    thug_matrix_rotate_y(p->body->orientation,turn);
    thug_matrix_rotate_y(p->cached_orientation,turn);
}
