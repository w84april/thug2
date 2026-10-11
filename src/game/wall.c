#include "skater.h"
#include "stats.h"
#include "collision_events.h"
#include "../audio/events.h"
#include "../core/matrix.h"
#include "../core/vector.h"
#include "../core/number.h"
#include "../core/timing.h"
#include "../script/delivery.h"
#include "../script/schedule.h"
#include "../platform/math.h"
#include <stddef.h>
#define R24 thug_platform_round_x87_single
_Static_assert(offsetof(ThugSkaterPhysics, rebound_gate_time) == 0x4e0, "Rebound gate timestamp");
_Static_assert(offsetof(ThugSkaterPhysics, last_rebound_time) == 0x4e4, "Last rebound timestamp");
_Static_assert(offsetof(ThugSkaterInput, button_1a0) == 0x1a0, "Rebound input");
_Static_assert(offsetof(ThugSkaterState, rebound_cancel_requested) == 0xb8, "Event cancellation flag");
_Static_assert(offsetof(ThugSkaterState, rebound_cancel_time) == 0xbc, "Cancellation timestamp");
_Static_assert(offsetof(ThugSkaterPhysics, sound) == 0x1514, "Wall impact sound component");
_Static_assert(offsetof(ThugSkaterPhysics, collision_events) == 0x1510, "Collision event component");
_Static_assert(offsetof(ThugSkaterPhysics, wall_gate) == 0x1530, "Wall response gate");
_Static_assert(offsetof(ThugSkaterWallGate, wall_response_suppressed) == 0x26, "Wall response suppression flag");

/* 0x004ff670. Event delivery precedes reading cancellation state or capturing
 * the velocity target. Rebuild the body and cached orientation only on rebound.
 * Numeric services and the full event dispatcher are the recovered callees;
 * the engine must supply initialized event state and concrete object handlers. */
uint8_t thug_skater_try_rebound(ThugSkaterPhysics *p, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!p->input->button_1a0.pressed) return 0;
    uint32_t previous = p->last_rebound_time;
    float age = (float)(thug_elapsed_time() + (thug_timer_offset - previous));
    if (thug_script_get_global_number(0x0017d543, 0) > age) return 0;
    const float *forward = p->body->orientation + 8, *normal = p->surface_probe.normal;
    double angle = R24(thug_script_get_global_number(0x1483fd01, 0) - 1);
    angle = R24(angle * (double)0.01745329238474369f);
    double threshold = -thug_platform_sin(angle);
    if (threshold <= thug_vector_dot(forward, normal)) return 0;
    previous = p->rebound_gate_time;
    age = (float)(thug_elapsed_time() + (thug_timer_offset - previous));
    if (thug_script_get_global_number(0x0017d543, 0) > age) return 0;
    thug_object_emit_event((ThugReferencedObject *)p->body, 0x4c03635b, NULL, diagnostics, memory);
    ThugSkaterState *state = p->state;
    if (state->rebound_cancel_requested) {
        state->rebound_cancel_requested = 0;
        state->rebound_cancel_time = thug_elapsed_time() + thug_timer_offset;
        return 0;
    }
    float *velocity = p->body->velocity, projected[4], reflected[4];
    float dot = (float)thug_vector_dot(velocity, normal);
    thug_vector_scaled(projected, dot, normal);
    thug_vector_scaled(reflected, 2, projected);
    thug_vector_subtract(velocity, reflected);
    ThugSkaterBody *body = p->body;
    double wide_speed = thug_vector_length(body->velocity);
    float speed = (float)wide_speed;
    if (wide_speed > (double)0.0010000000474974513f) {
        float reduced = (float)R24((double)speed - thug_script_get_global_number(0x1112fb1c, 0));
        float minimum = (float)thug_script_get_global_number(0xb78542c2, 0);
        float scale = (float)R24(thug_max_number(minimum, reduced) / speed);
        thug_vector_scale(body->velocity, scale);
    } else {
        float minimum = (float)-thug_script_get_global_number(0xb78542c2, 0);
        thug_vector_scaled(reflected, minimum, body->orientation + 8);
        thug_vector_copy(body->velocity, reflected);
    }
    thug_vector_project_preserve_length(p->body->velocity, p->orientation_target);
    thug_vector_copy(p->body->orientation + 8, p->body->velocity);
    thug_vector_normalize(p->body->orientation + 8);
    thug_vector_copy(p->body->orientation + 4, p->orientation_target);
    body = p->body;
    thug_vector_cross(reflected, body->orientation + 4, body->orientation + 8);
    thug_vector_copy(body->orientation, reflected);
    thug_matrix_copy(p->cached_orientation, p->body->orientation);
    p->last_rebound_time = thug_elapsed_time() + thug_timer_offset;
    return 1;
}

/* 0x005039f0. Turn velocity and both matrices toward a wall tangent. Return
 * the folded, unscaled angle; *turn receives the scaled angle before the
 * rotations. Velocity uses the wide angle, matrices reread the stored output.
 * Those rereads also retain the original behavior if output aliases the body. */
double thug_skater_wall_turn(ThugSkaterPhysics *p, const float normal[4], float *turn, float fraction) {
    const float *side = p->body->orientation;
    double dot = R24(R24(R24((double)side[2]*normal[2]) + R24((double)side[1]*normal[1])) + R24((double)normal[0]*side[0]));
    float cosine = (float)dot;
    if (dot > 1) cosine = 1;
    else if (cosine < -1) cosine = -1;
    double angle = thug_platform_acos_x87_single(cosine);
    float folded = (float)angle;
    if (angle > (double)1.5707963705062866f) folded -= 3.1415927410125732f;
    double scaled = thug_platform_multiply_x87_single(thug_script_get_global_number(0xe07ee1a9,1),folded);
    scaled = R24(scaled*fraction);
    *turn = (float)scaled;
    float *velocity = p->body->velocity;
    double sine = thug_platform_sin(scaled), cosine_turn = thug_platform_cos(scaled);
    float old_x = velocity[0];
    velocity[0] = (float)R24(R24(sine*velocity[2]) + R24(cosine_turn*velocity[0]));
    velocity[2] = (float)R24(R24(cosine_turn*velocity[2]) - R24(sine*old_x));
    thug_matrix_rotate_y(p->body->orientation,*turn);
    thug_matrix_rotate_y(p->cached_orientation,*turn);
    return folded;
}

/* 0x005059d0. Resolve the first wall contact, then perform the original second
 * probe. Events may replace the active body; the parameter source deliberately
 * remains the body captured before the first event. Explicit spills preserve
 * the x87 operation order through the segment construction and rotations. */
void thug_skater_wall_response(ThugSkaterPhysics *p, const float normal[4], ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (thug_skater_try_rebound(p, diagnostics, memory)) return;
    ThugSkaterBody *body = p->body;
    float direction[4], delta[3], offset[4], travel[4], turn;
    for (unsigned i = 0; i < 4; ++i)
        direction[i] = (float)R24((double)body->position[i] - body->previous_position[i]);
    for (unsigned i = 0; i < 3; ++i) delta[i] = direction[i];
    thug_vector_normalize(direction);
    body = p->body;
    const ThugSkaterBody *parameter_body = body;
    double height = thug_skater_get_parameter(0xd4205c9b, 1, parameter_body);
    for (unsigned i = 0; i < 4; ++i)
        offset[i] = (float)thug_platform_multiply_x87_single(height, body->orientation[4+i]);
    float folded = (float)thug_skater_wall_turn(p, normal, &turn, 1);
    double threshold = thug_platform_multiply_x87_single(thug_script_get_global_number(0x1483fd01, 1),
        0.01745329238474369f);
    double absolute = __builtin_fabs((double)folded);
    if (absolute > threshold) {
        body = p->body;
        const float *v = body->velocity;
        float speed = (float)R24(__builtin_sqrt(R24(R24(R24((double)v[0]*v[0]) +
            R24((double)v[1]*v[1])) + R24((double)v[2]*v[2]))));
        double factor = R24(1 - R24(R24(absolute-threshold) / R24((double)1.5707963705062866f-threshold)));
        for (unsigned i = 0; i < 4; ++i) body->velocity[i] = (float)R24(factor*body->velocity[i]);
        if (thug_script_get_global_number(0xbe0a58a0, 1) < speed) {
            uint32_t event = p->state->stat_modifier_selector == (folded < 0 ? 1 : 0) ? 0x756a7535 : 0xb4101d70;
            thug_object_emit_event((ThugReferencedObject *)p->body, event, NULL, diagnostics, memory);
            if (!p->parameter_mode_active) {
                uint32_t material = p->surface_probe.result.surface_metadata;
                double stat = thug_skater_stat_parameter(p->body, 0xcc5f87aa);
                float intensity = (float)R24((double)speed/stat);
                thug_sound_component_impact(p->sound, intensity, material, diagnostics, memory);
            } else {
                thug_script_run_sync(0xd478c96d, NULL, (ThugReferencedObject *)p->body, 0, diagnostics, memory);
            }
        }
    }
    body = p->body;
    float position[4];
    for (unsigned i = 0; i < 4; ++i) position[i] = (float)R24((double)p->surface_probe.point[i]-offset[i]);
    thug_vector_copy(body->position, position);
    body = p->body;
    double push[4];
    for (unsigned i = 0; i < 4; ++i) push[i] = R24((double)normal[i]*6);
    push[2] = (float)push[2]; push[3] = (float)push[3];
    for (unsigned i = 0; i < 4; ++i) body->position[i] = (float)R24(push[i]+body->position[i]);
    body = p->body;
    thug_vector_copy(direction, body->velocity);
    float distance = (float)R24(__builtin_sqrt(R24(R24(R24((double)delta[0]*delta[0]) +
        R24((double)delta[2]*delta[2])) + R24((double)delta[1]*delta[1]))));
    thug_vector_normalize(direction);
    for (unsigned i = 0; i < 4; ++i) travel[i] = (float)R24((double)direction[i]*distance);
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i] = (float)R24((double)offset[i]+body->position[i]);
    for (unsigned i = 0; i < 4; ++i) p->surface_segment[i] = (float)R24((double)offset[i]+p->surface_segment[i]);
    double extra = thug_skater_get_parameter(0x20102726, 1, parameter_body), extended[4];
    for (unsigned i = 0; i < 4; ++i) extended[i] = thug_platform_multiply_x87_single(extra, direction[i]);
    for (unsigned i = 0; i < 3; ++i) extended[i] = (float)extended[i];
    body = p->body;
    for (unsigned i = 0; i < 4; ++i) {
        double end = R24((double)offset[i]+body->position[i]);
        if (i >= 2) end = (float)end;
        float moved = (float)R24(end+travel[i]);
        p->surface_segment[4+i] = (float)R24((double)moved+extended[i]);
    }
    if (!thug_skater_query_surface(p, 0x10, 0, query) || !p->body->parameter_sets_enabled) return;
    double angle = R24((double)3.1415927410125732f-turn);
    turn = (float)angle;
    double sine = thug_platform_sin(angle), cosine = thug_platform_cos(angle);
    float *velocity = p->body->velocity, old_x = velocity[0];
    velocity[0] = (float)R24(R24(cosine*velocity[0]) + R24(sine*velocity[2]));
    velocity[2] = (float)R24(-R24(sine*old_x) + R24(cosine*velocity[2]));
    float *orientation = p->body->orientation, rotation[16];
    thug_matrix_rotation_y(rotation, turn);
    thug_matrix_multiply(orientation, rotation, orientation);
    thug_matrix_copy(p->cached_orientation, p->body->orientation);
    thug_vector_scale(p->body->velocity, .5f);
    if (thug_script_get_global_number(0xbe0a58a0, 1) < distance)
        thug_object_emit_event((ThugReferencedObject *)p->body, 0xb4101d70, NULL, diagnostics, memory);
}

/* 0x00506e50. Sweep the changed position through the original surface query.
 * Save the hit normal before collision scripts run: they can alter the probe,
 * replace the body or gate, and suppress the subsequent wall response. */
void thug_skater_movement_sweep(ThugSkaterPhysics *p, ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugSkaterBody *body = p->body;
    if (body->position[0] == body->previous_position[0] &&
        body->position[1] == body->previous_position[1] &&
        body->position[2] == body->previous_position[2] &&
        body->position[3] == body->previous_position[3]) return;
    float direction[4], offset[4];
    for (unsigned i = 0; i < 4; ++i)
        direction[i] = (float)R24((double)body->position[i]-body->previous_position[i]);
    thug_vector_normalize(direction);
    const ThugSkaterBody *parameter_body = p->body;
    double height = thug_skater_get_parameter(0xd4205c9b, 1, parameter_body);
    for (unsigned i = 0; i < 4; ++i)
        offset[i] = (float)thug_platform_multiply_x87_single(height, parameter_body->orientation[4+i]);
    body = p->body;
    for (unsigned i = 0; i < 4; ++i)
        p->surface_segment[i] = (float)R24((double)offset[i]+body->previous_position[i]);
    double extra = thug_skater_get_parameter(0x20102726, 1, parameter_body), extended[4];
    for (unsigned i = 0; i < 4; ++i) extended[i] = thug_platform_multiply_x87_single(extra, direction[i]);
    for (unsigned i = 0; i < 3; ++i) extended[i] = (float)extended[i];
    body = p->body;
    for (unsigned i = 0; i < 4; ++i) {
        double end = R24((double)offset[i]+body->position[i]);
        if (i) end = (float)end;
        p->surface_segment[4+i] = (float)R24(end+extended[i]);
    }
    if (!thug_skater_query_surface(p, 0x10, 0, query)) return;
    float normal[4];
    thug_vector_copy(normal, p->surface_probe.normal);
    if (p->surface_skatable) {
        const float *up = p->orientation_target;
        double dot = R24(R24(R24((double)normal[2]*up[2]) + R24((double)normal[1]*up[1])) +
            R24((double)normal[0]*up[0]));
        /* TEST AH,5 / JNP rejects only ordered less-than; NaN is accepted. */
        if (!(__builtin_fabs(dot) < (double)0.009999999776482582f)) {
            float push[4];
            for (unsigned i = 0; i < 4; ++i) push[i] = (float)R24((double)normal[i]*0.10000000149011612f);
            thug_vector_copy(p->body->position, p->surface_probe.point);
            thug_vector_add(p->body->position, push);
            return;
        }
    }
    static const uint32_t events[3] = {9, 0, 0}; /* Original 0x0064bbbc. */
    thug_collision_event_from_probe(p->collision_events, events, &p->surface_probe, diagnostics, memory);
    if (!p->wall_gate->wall_response_suppressed)
        thug_skater_wall_response(p, normal, query, diagnostics, memory);
}
