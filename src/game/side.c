#include "skater.h"
#include "objectives.h"
#include "collision_events.h"
#include "moving_contact.h"
#include "../audio/events.h"
#include "../core/vector.h"
#include "../core/matrix.h"
#include "../core/number.h"
#include "../core/timing.h"
#include "../platform/math.h"
#include "../script/delivery.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterPhysics, saved_probe) == 0x158, "Saved probe");
_Static_assert(offsetof(ThugSkaterPhysics, wall_transition_normal) == 0x38c, "Wall normal");
_Static_assert(offsetof(ThugSkaterPhysics, wall_transition_time) == 0x39c, "Wall time");
_Static_assert(offsetof(ThugSkaterPhysics, wall_transition_value) == 0x14cc, "Wall reset word");

/* 0x00506ba0. The assignment preserves original intrusive reference ordering. */
void thug_skater_save_surface(ThugSkaterPhysics *p, const ThugCollisionProbe *probe) {
    thug_collision_probe_assign(&p->saved_probe,probe);
    ((uint8_t *)p->sound)[0x1d] = ((uint8_t *)&p->saved_probe)[0x52];
}
static double angle(uint32_t name) {
    return thug_platform_multiply_x87_single(thug_script_get_global_number(name,1),0.01745329238474369f);
}
static float elapsed(uint32_t previous) {
    return (float)(int32_t)(thug_elapsed_time()+thug_timer_offset-previous);
}
/* 0x00508140. Complete wall transition, including its preliminary rising probe,
 * original event handlers, follow-up surface query and state/contact changes. */
uint8_t thug_skater_try_wall_transition(ThugSkaterPhysics *p, ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (p->parameter_mode_active || !p->surface_flag_4) return 0;
    if (!thug_skater_named_button(p->name_context,0x20689278)) {
        uint32_t window = thug_truncate_double_low_word(thug_platform_multiply_x87_single(
            thug_script_get_global_number(0x5d241b00,1),1000));
        if (!thug_skater_consume_recent_input(p->name_context,0x20689278,window,UINT32_MAX)) return 0;
    }
    float delta = elapsed(p->wall_transition_time);
    if (!(thug_platform_multiply_x87_single(thug_script_get_global_number(0xf0c74ec2,1),1000) < delta)) return 0;
    delta = elapsed(p->wall_transition_time_3a0);
    if (!(thug_platform_multiply_x87_single(thug_script_get_global_number(0xf0c74ec2,1),1000) < delta)) return 0;
    if (p->body->velocity[1] > 0) {
        float point[4], normal[4], displacement[4] = {0,0,0,1}, scaled[4], from[4], to[4];
        thug_vector_copy(point,p->surface_probe.point); thug_vector_copy(normal,p->surface_probe.normal);
        displacement[1] = (float)R24((double)p->body->velocity[1]*0.15000000596046448f);
        thug_vector_project_preserve_length(displacement,normal); thug_vector_add(point,displacement);
        thug_vector_scaled_copy(scaled,normal,6); thug_vector_difference(to,point,scaled);
        thug_vector_scaled_copy(scaled,normal,6); thug_vector_sum(from,point,scaled);
        ThugCollisionProbe probe; thug_collision_probe_from_points(&probe,from,to);
        uint8_t hit = thug_collision_probe_query(&probe,1,0,query);
        thug_collision_probe_release(&probe);
        if (!hit) return 0;
    }
    float horizontal_normal[4], direction[4], velocity[4];
    float *normal = p->wall_transition_normal;
    thug_vector_copy(normal,p->surface_probe.normal);
    thug_vector_copy(horizontal_normal,normal); horizontal_normal[1] = 0;
    thug_vector_normalize(horizontal_normal);
    ThugSkaterBody *body = p->body;
    thug_vector_copy(direction,body->velocity); direction[1] = 0; thug_vector_normalize(direction);
    thug_vector_copy(velocity,body->velocity); velocity[1] = 0;
    thug_vector_project_plane(velocity,horizontal_normal);
    float speed = (float)thug_vector_length(velocity);
    if (thug_script_get_global_number(0xf0636a67,1) > speed) return 0;
    float dot = (float)R24(R24(R24((double)direction[0]*horizontal_normal[0])+
        R24((double)direction[2]*horizontal_normal[2]))+R24((double)direction[1]*horizontal_normal[1]));
    if (!(-thug_platform_sin(angle(0xae23e850)) < normal[1])) return 0;
    if (!(thug_platform_sin(angle(0x6ac9f64d)) > __builtin_fabsf(dot))) return 0;
    body = p->body;
    if (!(thug_platform_cos(angle(0xbfcbb7e8)) < body->orientation[5])) return 0;
    if (!((const uint8_t *)p->name_context)[0x13b0])
        thug_skater_set_notification_flag(p->name_context,0,diagnostics,memory);
    thug_skater_save_surface(p,&p->surface_probe);
    static const uint32_t events[3] = {8,3,0};
    thug_collision_event_from_probe(p->collision_events,events,&p->saved_probe,diagnostics,memory);
    if (p->wall_gate->wall_response_suppressed) return 0;
    float point[4], move[4], scaled[4], end[4];
    thug_vector_copy(point,p->surface_probe.point);
    thug_vector_difference(move,p->body->position,p->body->previous_position);
    thug_vector_project_preserve_length(move,normal);
    thug_vector_copy(p->surface_segment,p->body->position);
    thug_vector_scaled_copy(scaled,move,3); thug_vector_sum(end,p->body->position,scaled);
    thug_vector_copy(p->surface_segment+4,end);
    if (thug_skater_query_surface(p,0x10,0,query)) return 0;
    p->wall_transition_time = thug_elapsed_time()+thug_timer_offset;
    thug_vector_copy(p->body->position,point); thug_vector_add(p->body->position,normal);
    thug_vector_project_preserve_length(p->body->velocity,normal);
    body = p->body; thug_vector_copy(body->orientation+8,body->velocity);
    thug_vector_normalize(p->body->orientation+8);
    thug_vector_copy(p->body->orientation+4,normal);
    body = p->body; thug_vector_cross(move,body->orientation+4,body->orientation+8);
    thug_vector_copy(body->orientation,move); thug_vector_normalize(p->body->orientation);
    thug_matrix_copy(p->cached_orientation,p->body->orientation);
    body = p->body;
    double side = R24(R24(R24(-(double)normal[2]*body->velocity[0])+
        R24((double)normal[0]*body->velocity[2]))+R24((double)body->velocity[1]*0));
    thug_object_emit_event((ThugReferencedObject *)body,side < 0 ? 0x5de19c83 : 0x51372712,0,diagnostics,memory);
    thug_skater_change_state(p,2,diagnostics,memory);
    thug_skater_adjust_moving_contact(p,memory);
    p->wall_transition_value = 0;
    return 1;
}

/* 0x0050a2c0. Side contact may update position yet return false. Only the
 * successful wall transition or accepted standing correction returns true. */
uint8_t thug_skater_correct_side(ThugSkaterPhysics *p, float direction, float distance,
    ThugCollisionQuery *query, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (p->state->mode == 2) return 0;
    ThugSkaterBody *body = p->body;
    double height = thug_script_get_global_number(0xb45b39e2,1);
    float offset[4], endpoint[4];
    for (unsigned i = 0; i < 4; ++i) offset[i] = (float)thug_platform_multiply_x87_single(height,body->orientation[i+4]);
    thug_vector_sum(p->surface_segment,offset,p->body->position);
    float extended = distance;
    if (p->state->mode == 1) extended = (float)R24(thug_script_get_global_number(0x1c58c8b4,1)+(double)distance);
    body = p->body;
    for (unsigned i = 0; i < 4; ++i) {
        double lane = R24((double)direction*body->orientation[i]);
        if (i < 2) lane = (float)lane;
        offset[i] = (float)R24(lane*extended);
    }
    thug_vector_sum(p->surface_segment+4,offset,p->surface_segment);
    if (!thug_skater_query_surface(p,0x10,0,query)) return 0;
    float normal[4]; thug_vector_copy(normal,p->surface_probe.normal);
    if (p->state->mode == 1) {
        if (!p->state->unknown_e0 && !p->state->resistance_requested &&
            thug_skater_try_wall_transition(p,query,diagnostics,memory)) return 1;
        float difference[4]; thug_vector_difference(difference,p->surface_probe.point,p->surface_segment);
        double square = R24(R24(R24((double)difference[2]*difference[2])+
            R24((double)difference[1]*difference[1]))+R24((double)difference[0]*difference[0]));
        double remaining = R24(R24(__builtin_sqrt(square))-R24((double)extended-distance));
        float turn = (float)remaining;
        if (remaining > 0) {
            thug_vector_set_length(difference,turn); thug_vector_divided(offset,difference,10);
            thug_vector_subtract(p->body->position,offset);
            ThugSkaterInput *input = p->input;
            if (p->state->mode != 1 && !input->button_100.pressed && !input->button_a0.pressed &&
                !input->button_60.pressed && !input->button_80.pressed)
                thug_skater_wall_turn(p,normal,&turn,0.20000000298023224f);
        }
        return 0;
    }
    body = p->body;
    double dot = thug_vector_dot(normal,body->orientation+4);
    if (!(dot < 0.25 && dot > -0.25)) return 0;
    thug_vector_copy(body->position,p->side_previous_position);
    thug_skater_wall_turn(p,normal,&extended,0.20000000298023224f);
    thug_vector_scaled_copy(offset,normal,distance);
    float to[4]; thug_vector_sum(to,p->surface_probe.point,offset);
    thug_vector_sum(endpoint,p->surface_probe.point,normal);
    ThugCollisionProbe probe; thug_collision_probe_from_points(&probe,endpoint,to);
    uint8_t hit = thug_collision_probe_query(&probe,1,0,query);
    if (!hit) {
        static const uint32_t events[3] = {9,0,0};
        thug_collision_event_from_probe(p->collision_events,events,&p->surface_probe,diagnostics,memory);
        if (!p->wall_gate->wall_response_suppressed) {
            body = p->body;
            float stored_height = (float)thug_script_get_global_number(0xb45b39e2,1);
            thug_vector_scaled_copy(offset,body->orientation+4,stored_height);
            thug_vector_difference(endpoint,probe.segment+4,offset);
            thug_vector_copy(body->position,endpoint);
            thug_collision_probe_release(&probe); return 1;
        }
    }
    thug_collision_probe_release(&probe); return 0;
}
/* 0x0050c930. A second-side success can require a third probe. Revert the
 * captured position only when both opposing corrections report success. */
void thug_skater_correct_sides(ThugSkaterPhysics *p, ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    float position[4]; thug_vector_copy(position,p->body->position);
    float distance = (float)thug_script_get_global_number(0x406b425f,1);
    if (thug_skater_correct_side(p,-1,distance,query,diagnostics,memory)) {
        if (thug_skater_correct_side(p,1,distance,query,diagnostics,memory)) thug_vector_copy(p->body->position,position);
    } else if (thug_skater_correct_side(p,1,distance,query,diagnostics,memory) &&
               thug_skater_correct_side(p,-1,distance,query,diagnostics,memory)) thug_vector_copy(p->body->position,position);
}
