#include "skater.h"

ThugComponentTypeRegistry *thug_component_type_registry; /* 006f0fb8 */
void *thug_component_type_heads[128]; /* 006f0db8 */
/* 0x0045f2d0. Registry order indexes a separate global list of type heads.
 * Registered counts must fit that fixed table, as in the original manager. */
void *thug_component_type_head(const ThugComponentTypeRegistry *registry,uint32_t type) {
    for(uint32_t i=0;i<registry->count;++i)
        if(registry->entries[i].type==type)return thug_component_type_heads[i];
    return 0;
}
/* 0x0057c4f0. The marker write precedes the overlapping forward matrix copy. */
float *thug_transform_set(ThugObjectTransform *target,const float source[16]) {
    target->changed=1;
    return thug_matrix_copy(target->matrix,source);
}
/* 0x0042ba10. Retain the captured matrix across the owned-transform update. */
float *thug_component_world_transform(ThugTransformComponent *component,float out[16]) {
    ThugSkaterBody *body=component->base.owner;
    float matrix[16];thug_matrix_copy(matrix,body->orientation);
    matrix[3]=matrix[7]=matrix[11]=0;
    matrix[12]=body->position[0];matrix[13]=body->position[1];matrix[14]=body->position[2];matrix[15]=1;
    thug_transform_set(component->transform,matrix);
    thug_matrix_copy(out,matrix);return out;
}
#include "stats.h"
#include "objectives.h"
#include "../audio/events.h"
#include "../core/timing.h"
#include "../core/vector.h"
#include "../core/matrix.h"
#include "../platform/math.h"
#include "../script/delivery.h"
#include <stddef.h>

_Static_assert(offsetof(ThugSkaterBody, velocity) == 0xac, "Skater velocity offset");
_Static_assert(offsetof(ThugSkaterPhysics, time_step) == 0x8c, "Physics timestep offset");
_Static_assert(offsetof(ThugSkaterPhysics, nearby_obstacle_direction) == 0x2d4, "Obstacle direction offset");
_Static_assert(offsetof(ThugSkaterPhysics, friction) == 0x314, "Physics friction offset");
_Static_assert(offsetof(ThugSkaterPhysics, surface_probe) == 0xa8, "Surface probe offset");
_Static_assert(offsetof(ThugSkaterPhysics, surface_segment) == 0x208, "Surface segment offset");
_Static_assert(offsetof(ThugSkaterPhysics, surface_skatable) == 0x228, "Surface flags offset");
_Static_assert(offsetof(ThugSkaterPhysics, orientation_source) == 0x58, "Orientation source offset");
_Static_assert(offsetof(ThugSkaterPhysics, orientation_blend) == 0x88, "Orientation blend offset");
_Static_assert(offsetof(ThugSkaterPhysics, cached_orientation) == 0x18, "Cached matrix offset");
_Static_assert(offsetof(ThugSkaterPhysics, ground_transition_flag) == 0x2d0, "Ground transition flag offset");
_Static_assert(offsetof(ThugSkaterPhysics, ground_gate) == 0x152c, "Ground gate pointer offset");
_Static_assert(offsetof(ThugSkaterState, ground_transition_time) == 0x34, "Transition time offset");
_Static_assert(offsetof(ThugSkaterState, skip_ground_probe) == 0x78, "Ground skip flag offset");
_Static_assert(offsetof(ThugSkaterState, ground_contact_time) == 0x84, "Ground contact time offset");
_Static_assert(offsetof(ThugSkaterState, base.owner) == 0xc, "State owner offset");
_Static_assert(offsetof(ThugSkaterState, mode) == 0x18, "State mode offset");
_Static_assert(offsetof(ThugSkaterState, material) == 0xe1, "State material offset");
_Static_assert(offsetof(ThugSkaterState, surface_flag_8) == 0x40, "State surface flag offset");
_Static_assert(offsetof(ThugSkaterState, transition_time_6c) == 0x6c, "State transition time offset");
_Static_assert(offsetof(ThugSkaterPhysics, transition_previous_position) == 0x268, "Transition position offset");
_Static_assert(offsetof(ThugSkaterPhysics, transition_height) == 0x298, "Transition height offset");
_Static_assert(offsetof(ThugSkaterPhysics, state_change_time) == 0x90, "State change timestamp");
_Static_assert(offsetof(ThugSkaterPhysics, state_saved_position) == 0x258, "Saved state position");
_Static_assert(offsetof(ThugSkaterPhysics, state_value_30c) == 0x30c, "State reset word");
_Static_assert(offsetof(ThugSkaterPhysics, state_exit_time) == 0x384, "State exit timestamp");
_Static_assert(offsetof(ThugSkaterState, state_time_5c) == 0x5c, "State flag timestamp");
_Static_assert(offsetof(ThugSkaterState, state_time_dc) == 0xdc, "State flag timestamp");
_Static_assert(offsetof(ThugSoundComponent, state) == 0x18, "Sound state");
_Static_assert(offsetof(ThugSoundComponent, state_flag) == 0x1e, "Sound state flag");

/* 0x004fded0. Gameplay notification precedes the mode event. Re-read component
 * pointers after callbacks; the final sound-state write uses the then-current one. */
void thug_skater_change_state(ThugSkaterPhysics *p, uint32_t mode,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugSkaterState *state = p->state;
    if (state->mode != mode) {
        p->state_change_time = thug_elapsed_time()+thug_timer_offset;
        state = p->state; p->previous_state = state->mode;
    }
    if (state->mode == 3 && mode != 3 &&
        (p->state_saved_position[0] != 0 || p->state_saved_position[1] != 0 || p->state_saved_position[2] != 0)) {
        thug_vector_copy(p->body->position,p->state_saved_position);
        thug_vector_copy(p->body->previous_position,p->body->position);
    }
    if (mode != 3) {
        p->state_saved_position[0] = p->state_saved_position[1] = p->state_saved_position[2] = 0;
        p->state_saved_position[3] = 1;
    }
    if (mode) thug_skater_set_notification_flag(p->name_context,1,diagnostics,memory);
    state = p->state;
    if (state->mode == 4 && mode != 4) {
        if (state->state_flag_58) {
            state->state_flag_58 = 0; state->state_time_5c = thug_elapsed_time()+thug_timer_offset;
        }
        p->sound->state_flag = 0;
    }
    if (p->state->mode == 1) {
        if (mode != 1) {
            uint32_t time = thug_elapsed_time()+thug_timer_offset;
            state = p->state; p->state_exit_time = time;
            if (state->state_flag_c0) {
                state->state_flag_c0 = 0; state->state_time_c4 = thug_elapsed_time()+thug_timer_offset;
            }
            state = p->state;
            if (state->state_flag_d0) {
                state->state_flag_d0 = 0; state->state_time_d4 = thug_elapsed_time()+thug_timer_offset;
            }
            state = p->state;
            if (state->state_flag_d8) {
                state->state_flag_d8 = 0; state->state_time_dc = thug_elapsed_time()+thug_timer_offset;
            }
        }
    } else if (mode == 1) {
        if (p->state->mode != 2) p->state_enter_time = thug_elapsed_time()+thug_timer_offset;
        uint32_t zero = 0; __builtin_memcpy((uint8_t *)p->name_context+0x13a4,&zero,4);
        thug_input_button_clear_latch(&p->input->button_a0);
        thug_input_button_clear_latch(&p->input->button_100);
        p->state_value_30c = 0;
    }
    thug_skater_state_set_mode(p->state,mode,diagnostics,memory);
    p->sound->state = mode;
}

/* 0x00519660 / 0x005196a0. Store before delivery; callback mutations survive. */
void thug_skater_state_set_mode(ThugSkaterState *state, uint32_t mode,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (state->mode == mode) return;
    state->mode = mode;
    thug_object_emit_event(state->base.owner, 0xa7662059, 0, diagnostics, memory);
}
void thug_skater_state_set_material(ThugSkaterState *state, uint32_t value,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    uint8_t material = (uint8_t)value;
    if (state->material == material) return;
    state->material = material;
    thug_object_emit_event(state->base.owner, 0xd3fde02a, 0, diagnostics, memory);
}

const ThugSkaterOrientationContext *thug_skater_orientation_context;

const char thug_skater_tracking_format[] = "Tracking%d %.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n";
/* 0x004fc4a0. Disabled tracking does not read either vector. */
void thug_skater_track_movement(uint32_t type, const float from[4], const float to[4], const ThugDiagnostics *diagnostics) {
    if (thug_script_get_global_integer(0x19fb78fa, 1))
        diagnostics->print(diagnostics->context, thug_skater_tracking_format, type,
            (double)from[0], (double)from[1], (double)from[2], (double)to[0], (double)to[1], (double)to[2]);
}

/* 0x004feba0. Preserve the original snapshots, horizontal threshold, distinct
 * X/product spill order, and per-flag timestamp updates. */
void thug_skater_prepare_floor_transition(ThugSkaterPhysics *physics, ThugCollisionQuery *query,
    const ThugDiagnostics *diagnostics) {
    ThugSkaterState *state = physics->state;
    if (state->surface_flag_8) {
        thug_skater_track_movement(3, physics->body->previous_position, physics->body->position, diagnostics);
        float up[4];
        thug_vector_copy(up, physics->orientation_target);
        thug_vector_copy(physics->transition_orientation, physics->orientation_target);
        thug_vector_copy(physics->transition_previous_position, physics->body->previous_position);
        physics->transition_previous_position[1] -= 1;
        up[1] = 0;
        double z2 = thug_platform_round_x87_single((double)up[2]*up[2]);
        double x2 = thug_platform_round_x87_single((double)up[0]*up[0]);
        double length = thug_platform_round_x87_single(__builtin_sqrt(thug_platform_round_x87_single(z2+x2)));
        if (length > 0.0010000000474974513f) {
            thug_vector_normalize(up);
            thug_vector_project_preserve_length(physics->body->velocity, up);
            thug_skater_set_up_vector(physics, up[0], up[1], up[2], up[3], query);
            thug_vector_copy(physics->transition_forward, physics->body->orientation+8);
            /* FLD/FCHS/FSTP quiets signaling NaNs as well as flipping sign. */
            uint32_t word;
            __builtin_memcpy(&word, physics->transition_forward+1, 4);
            if ((word & 0x7f800000) == 0x7f800000 && (word & 0x7fffff)) word |= 0x400000;
            word ^= 0x80000000;
            __builtin_memcpy(physics->transition_forward+1, &word, 4);
            double distance = thug_script_get_global_number(0x78384871, 1), scaled[4];
            for (unsigned i = 0; i < 4; ++i) {
                scaled[i] = thug_platform_multiply_x87_single(distance, up[i]);
                if (i) scaled[i] = (float)scaled[i];
            }
            for (unsigned i = 0; i < 4; ++i)
                physics->body->position[i] = (float)thug_platform_round_x87_single(scaled[i]+physics->body->position[i]);
            state = physics->state;
            if (state->ground_transition_flag != 1) {
                state->ground_transition_flag = 1;
                state->ground_transition_time = thug_elapsed_time()+thug_timer_offset;
            }
            state = physics->state;
            if (state->transition_flag_38 != 1) {
                state->transition_flag_38 = 1;
                state->transition_time_3c = thug_elapsed_time()+thug_timer_offset;
            }
            state = physics->state;
            if (state->transition_flag_68 != 1) {
                state->transition_flag_68 = 1;
                state->transition_time_6c = thug_elapsed_time()+thug_timer_offset;
            }
            physics->transition_height = 6;
            return;
        }
        state = physics->state;
    }
    if (state->ground_transition_flag) {
        state->ground_transition_flag = 0;
        state->ground_transition_time = thug_elapsed_time()+thug_timer_offset;
    }
}

/* 0x004fea50. Blend the target/previous up vectors, then update the cached
 * basis. Side and forward rows are copied back from the body after repairing
 * the cache, in the original order; the body's matrix itself is not changed. */
void thug_skater_blend_orientation(ThugSkaterPhysics *physics) {
    if (physics->orientation_blend != 0) {
        if (thug_vector_equal(physics->orientation_previous, physics->orientation_target))
            physics->orientation_blend = 0;
        else {
            double rate = thug_script_get_global_number(0xd8120182, 1);
            double decrement = thug_platform_multiply_x87_single(rate, physics->time_step);
            decrement = thug_platform_round_x87_single(decrement*60.0);
            double remaining = thug_platform_round_x87_single((double)physics->orientation_blend-decrement);
            physics->orientation_blend = (float)remaining;
            if (remaining <= 0) {
                physics->orientation_blend = 0;
                thug_vector_copy(physics->orientation_source, physics->orientation_target);
            } else {
                float value[4];
                thug_vector_lerp(value, physics->orientation_target, physics->orientation_previous, (float)remaining);
                thug_vector_copy(physics->orientation_source, value);
                thug_vector_normalize(physics->orientation_source);
            }
        }
    }
    if (thug_vector_not_equal(physics->cached_orientation+4, physics->orientation_source)) {
        thug_vector_copy(physics->cached_orientation+4, physics->orientation_source);
        thug_matrix_orthogonalize(physics->cached_orientation, 1);
        thug_vector_copy(physics->cached_orientation, physics->body->orientation);
        thug_vector_copy(physics->cached_orientation+8, physics->body->orientation+8);
    }
}

/* 0x00504b40. A downward hit with flag 8 or a normal below 0.2 is ignored.
 * The upright test includes unordered values, matching TEST AH,41 / JE. */
void thug_skater_ground_update(ThugSkaterPhysics *physics, ThugCollisionQuery *query_state) {
    if (physics->state->skip_ground_probe) return;
    if (physics->body->velocity[1] > 0 && physics->ground_gate->contact) return;
    ThugCollisionProbe probe;
    thug_collision_probe_initialize(&probe);
    for (unsigned i = 0; i < 4; ++i) probe.segment[i] = probe.segment[i+4] = physics->body->position[i];
    probe.segment[5] -= 500;
    if (thug_collision_probe_query(&probe, 1, 0, query_state)
            && !(probe.result.surface_flags & 8) && !(probe.normal[1] < 0.2f)) {
        ThugSkaterState *state = physics->state;
        if (state->ground_transition_flag) {
            state->ground_transition_flag = 0;
            state->ground_transition_time = thug_elapsed_time() + thug_timer_offset;
            physics->ground_transition_flag = 0;
        }
        state = physics->state;
        if (state->ground_contact_flag != 1) {
            state->ground_contact_flag = 1;
            state->ground_contact_time = thug_elapsed_time() + thug_timer_offset;
        }
        if (!(physics->body->orientation[5] > 0.9f)) {
            float rate = (float)thug_skater_stat_parameter(physics->body, 0xe7116a96);
            ThugSkaterBody *body = physics->body;
            float horizontal[4] = { body->orientation[4], 0, body->orientation[6], body->orientation[7] };
            thug_vector_normalize(horizontal);
            float axis[4] = { -horizontal[2], 0, horizontal[0], 0 };
            thug_matrix_rotate_axis(body->orientation, axis, rate * physics->time_step);
            thug_matrix_copy(physics->cached_orientation, physics->body->orientation);
        }
    }
    thug_collision_probe_release(&probe);
}

/* 0x004fe860. Parameters are passed by value in the original. An upward probe
 * may replace the requested vector with world-up before checking for a change.
 * The context identifier's meaning is not yet recovered. */
void thug_skater_set_up_vector(ThugSkaterPhysics *physics, float x, float y, float z, float w,
    ThugCollisionQuery *query_state) {
    float up[4] = { x, y, z, w };
    if (thug_skater_orientation_context->identifier != 0xd443a2bc && y > 0) {
        float end[4];
        for (unsigned i = 0; i < 4; ++i) end[i] = up[i] * 72.0f + physics->body->position[i];
        ThugCollisionProbe probe;
        thug_collision_probe_from_points(&probe, physics->body->position, end);
        if (thug_collision_probe_query(&probe, 1, 0, query_state)) {
            up[0] = 0; up[1] = 1; up[2] = 0; up[3] = 1;
        }
        if (probe.moving_object.object) thug_object_reference_unlink(probe.moving_object.object, &probe.moving_object);
    }
    if (thug_vector_not_equal(up, physics->orientation_target)) {
        for (unsigned i = 0; i < 4; ++i) physics->orientation_target[i] = up[i];
        for (unsigned i = 0; i < 4; ++i) physics->orientation_previous[i] = physics->orientation_source[i];
        physics->orientation_blend = 1;
        for (unsigned i = 0; i < 4; ++i) physics->body->orientation[i + 4] = up[i];
        thug_matrix_orthogonalize(physics->body->orientation, 1);
    }
}

/* 0x005003a0. A miss leaves the classification bytes unchanged. Flags take
 * precedence in the order 1, 2, 8, 4; otherwise compare the normal to the script
 * angle's sine. Keep this comparison in double: rounding the sine to float can
 * change the classification at a boundary. NaNs take the original accepted path. */
uint8_t thug_skater_query_surface(ThugSkaterPhysics *physics, uint16_t excluded, uint16_t required,
    ThugCollisionQuery *query_state) {
    ThugCollisionProbe *probe = &physics->surface_probe;
    thug_collision_probe_set_points(probe, physics->surface_segment, physics->surface_segment + 4);
    thug_collision_probe_set_flags(probe, excluded, required);
    uint8_t found = thug_collision_probe_query(probe, 1, 0, query_state);
    if (!found) return 0;
    thug_skater_classify_surface(physics);
    return found;
}

void thug_skater_classify_surface(ThugSkaterPhysics *physics) {
    ThugCollisionProbe *probe = &physics->surface_probe;
    if (probe->result.checksum && probe->result.flag_40) probe->result.unknown_38 = 0;
    uint16_t flags = probe->result.surface_flags;
    float normal_y = probe->normal[1];
    physics->surface_flag_4 = 0;
    physics->surface_flag_8 = (flags >> 3) & 1;
    if (flags & 1) physics->surface_skatable = 1;
    else if (flags & 2) physics->surface_skatable = 0;
    else if (flags & 8) physics->surface_skatable = 1;
    else if (flags & 4) { physics->surface_skatable = 0; physics->surface_flag_4 = 1; }
    else {
        double angle = thug_script_get_global_number(0x3eede4d3, 1);
        double radians = thug_platform_multiply_x87_single(angle, 0.01745329238474369f);
        physics->surface_skatable = !(thug_platform_sin(radians) > (double)normal_y);
    }
}

static void stop(float velocity[4]) {
    velocity[0] = velocity[1] = velocity[2] = 0; velocity[3] = 1;
}

/* 0x004fe1f0. Drag magnitude is proportional to speed squared. Keep the two
 * distinct sum orders and the original W behavior (normalization retains W,
 * so an unsaturated drag subtraction subtracts the original W from itself). */
void thug_skater_apply_quadratic_drag(ThugSkaterPhysics *physics, float coefficient) {
    float *v = physics->body->velocity;
    float speed2 = (v[0] * v[0] + v[1] * v[1]) + v[2] * v[2];
    if (speed2 < 0.00001f) return;
    float decrement[4] = { v[0], v[1], v[2], v[3] };
    float magnitude = ((speed2 * physics->time_step) * coefficient) * 60.0f;
    thug_vector_set_length(decrement, magnitude);
    float d2 = (decrement[2] * decrement[2] + decrement[0] * decrement[0]) + decrement[1] * decrement[1];
    if (d2 > speed2) stop(v);
    else for (unsigned i = 0; i < 4; ++i) v[i] -= decrement[i];
}

/* 0x004fe730. Fixed-magnitude velocity reduction; prevents overshoot. The
 * x87 unordered branches proceed with arithmetic rather than forcing a stop. */
void thug_skater_apply_friction(ThugSkaterPhysics *physics) {
    float *v = physics->body->velocity;
    float speed = __builtin_sqrtf((v[2] * v[2] + v[1] * v[1]) + v[0] * v[0]);
    if (speed < 0.0001f) { stop(v); return; }
    float scale = ((physics->time_step / speed) * physics->friction) * 60.0f;
    float d[4] = { scale * v[0], v[1] * scale, v[2] * scale, v[3] * scale };
    float d2 = (d[2] * d[2] + d[1] * d[1]) + d[0] * d[0];
    if (speed * speed < d2) stop(v);
    else for (unsigned i = 0; i < 4; ++i) v[i] -= d[i];
}

/* 0x005009c0. Four 12-unit probes along +/-Z and +/-X of the skater's basis.
 * Strictly closer hits replace the direction; ties keep the earlier direction.
 * The checksums are the original direction identifiers (last two: left/right). */
void thug_skater_nearby_obstacle(ThugSkaterPhysics *physics, ThugCollisionQuery *query_state) {
    const uint32_t directions[4] = { 0x7f03932c, 0x83c84ba2, 0x85981897, 0x4b358aeb };
    ThugCollisionProbe probe;
    thug_collision_probe_initialize(&probe);
    physics->nearby_obstacle_direction = 0;
    for (unsigned i = 0; i < 4; ++i) probe.segment[i] = physics->body->position[i];
    float closest = 999.0f;
    for (unsigned direction = 0; direction < 4; ++direction) {
        const float *axis = physics->body->orientation + (direction < 2 ? 8 : 0);
        float length = direction % 2 ? -12.0f : 12.0f;
        for (unsigned i = 0; i < 4; ++i) probe.segment[i + 4] = probe.segment[i] + length * axis[i];
        if (thug_collision_probe_query(&probe, 1, 0, query_state) && probe.fraction < closest) {
            closest = probe.fraction;
            physics->nearby_obstacle_direction = directions[direction];
        }
    }
    if (probe.moving_object.object) thug_object_reference_unlink(probe.moving_object.object, &probe.moving_object);
}

/* 0x004fd660, a script-facing skater obstruction query. Optional unnamed
 * distance defaults to 200; only the XYZ direction is normalized. */
uint8_t thug_skater_forward_obstruction(ThugSkaterPhysics *physics, const ThugScriptStructure *parameters,
    uint32_t unused, ThugCollisionQuery *query_state) {
    (void)unused;
    float distance = 200;
    thug_script_get_float(parameters, 0, &distance, 0);
    ThugCollisionProbe probe;
    thug_collision_probe_initialize(&probe);
    for (unsigned i = 0; i < 4; ++i) probe.segment[i] = physics->body->position[i];
    float x = physics->body->orientation[8], y = physics->body->orientation[9], z = physics->body->orientation[10];
    float length = __builtin_sqrtf((z * z + y * y) + x * x);
    if (length > 0) { float inverse = 1 / length; x *= inverse; y *= inverse; z *= inverse; }
    probe.segment[4] = x * distance + probe.segment[0];
    probe.segment[5] = y * distance + probe.segment[1];
    probe.segment[6] = z * distance + probe.segment[2];
    probe.segment[7] = probe.segment[3];
    uint8_t found = thug_collision_probe_query(&probe, 1, 0, query_state)
        && !(probe.result.surface_flags & 8) && !(__builtin_fabsf(probe.normal[1]) > 0.1f);
    if (probe.moving_object.object) thug_object_reference_unlink(probe.moving_object.object, &probe.moving_object);
    return found;
}
