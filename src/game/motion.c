#include "skater.h"
#include "stats.h"
#include "../core/vector.h"
#include "../core/matrix.h"
#include "../platform/math.h"
#include "../core/checksum.h"
#include "../core/timing.h"
#include "../script/delivery.h"
#include "../script/schedule.h"
#include <stddef.h>

_Static_assert(offsetof(ThugSkaterPhysics, acceleration_requested) == 0x2d9, "Acceleration request");
_Static_assert(offsetof(ThugSkaterPhysics, alternate_acceleration) == 0x303, "Alternate acceleration");
_Static_assert(offsetof(ThugSkaterPhysics, acceleration_blocked) == 0x310, "Acceleration gate");
_Static_assert(offsetof(ThugSkaterPhysics, brake_input_enabled) == 0x311, "Brake input gate");
_Static_assert(offsetof(ThugSkaterPhysics, braking) == 0x324, "Braking flag");
_Static_assert(offsetof(ThugSkaterPhysics, accelerate_along_velocity) == 0x388, "Acceleration direction");
_Static_assert(offsetof(ThugSkaterPhysics, input) == 0x150c, "Input pointer");
_Static_assert(offsetof(ThugSkaterInput, button_180) == 0x180, "Input button offset");
_Static_assert(offsetof(ThugSkaterState, resistance_requested) == 0x70, "Resistance flag");
_Static_assert(offsetof(ThugSkaterState, drag_selector_time) == 0x24, "Drag selector timestamp");
_Static_assert(offsetof(ThugSkaterPhysics, input_release_elapsed) == 0x378, "Input release elapsed");
_Static_assert(offsetof(ThugSkaterPhysics, turn_positive) == 0x3a5, "Turn direction flag");
_Static_assert(offsetof(ThugSkaterPhysics, name_context) == 0x1518, "Name context");
_Static_assert(offsetof(ThugSkaterPhysics, mode_context) == 0x1524, "Mode context");

static double r24(double x) { return thug_platform_round_x87_single(x); }
/* Inlined x87 length sequence in the braking/eligibility/alignment routines.
 * PC=24 retains a wider exponent until the caller's explicit float store. */
static double speed(const float v[4]) {
    double sum = r24(r24((double)v[0] * v[0]) + r24((double)v[1] * v[1]));
    return r24(__builtin_sqrt(r24(sum + r24((double)v[2] * v[2]))));
}

/* The parameter getter returns an exact int32 or float32. Integer squares can
 * exceed double's exact precision, so round their exact product directly. */
static double parameter_square(double value) {
    if (value >= -0x1p31 && value <= 0x1p31-1 && value == (int32_t)value) {
        int64_t integer = (int32_t)value;
        uint64_t product = (uint64_t)(integer*integer);
        if (product > 0xffffff) {
            unsigned shift = 64-__builtin_clzll(product)-24;
            uint64_t kept = product>>shift, tail = product & ((UINT64_C(1)<<shift)-1), half = UINT64_C(1)<<(shift-1);
            if (tail > half || (tail == half && (kept & 1))) ++kept;
            product = kept<<shift;
        }
        return (double)product;
    }
    return r24(value*value);
}

/* 0x00503560. Left input has priority. The fast-turn ramp uses a signed
 * elapsed value and a spilled rate only on its low-speed path. */
void thug_skater_steer(ThugSkaterPhysics *p) {
    ThugSkaterBody *body = p->body;
    float magnitude = (float)speed(body->velocity);
    ThugSkaterInput *input = p->input;
    ThugInputButton *button = input->button_60.pressed ? &input->button_60 : &input->button_80;
    if (!button->pressed) return;
    double rate = thug_skater_get_parameter(input->button_40.pressed ? 0x7933a8ef : 0x374e056b, 1, body);
    if (button == &input->button_80) rate = -rate;
    uint8_t rounded = 0;
    if (input->button_40.pressed && magnitude < 10) {
        float stored = (float)rate;
        int32_t elapsed = (int32_t)thug_input_button_elapsed(button);
        rate = elapsed < 600 ? r24(thug_platform_multiply_x87_single(elapsed, stored)*0.0016666667070239782f) : stored;
        rounded = 1;
    }
    if (rate == 0) return;
    double angle = rounded ? r24(rate*p->time_step) : thug_platform_multiply_x87_single(rate, p->time_step);
    float stored_angle = (float)angle;
    p->turn_positive = angle > 0;
    if (!p->accelerate_along_velocity) {
        float *velocity = p->body->velocity;
        double sine = thug_platform_sin(stored_angle), cosine = thug_platform_cos(stored_angle);
        double x = velocity[0];
        velocity[0] = (float)r24(r24(cosine*x)+r24(sine*velocity[2]));
        velocity[2] = (float)r24(r24(cosine*velocity[2])-r24(x*sine));
    }
    float rotation[16];
    thug_matrix_rotation_y(rotation, stored_angle);
    thug_matrix_multiply(p->body->orientation, rotation, p->body->orientation);
    thug_matrix_rotation_y(rotation, stored_angle);
    thug_matrix_multiply(p->cached_orientation, rotation, p->cached_orientation);
}

/* 0x004ff920. Reverse the four side/forward rows, or request the original
 * mode-specific script once. Synchronous scripts may mutate this component. */
void thug_skater_handle_backward_motion(ThugSkaterPhysics *p, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugSkaterBody *body = p->body;
    if (p->state->resistance_requested || p->state->moving_contact_locked || p->braking) return;
    if (!(thug_vector_dot(body->velocity, body->orientation+8) < 0)) return;
    double threshold = thug_skater_get_parameter(0x2bf71eeb, 1, body);
    const float *v = body->velocity;
    double squared = r24(r24(r24((double)v[0]*v[0])+r24((double)v[1]*v[1]))+r24((double)v[2]*v[2]));
    if (!(parameter_square(threshold) < squared)) return;
    if (p->parameter_mode_active || p->mode_context->identifier == 0xef24413b || p->mode_context->identifier == 0x0ac90769) {
        uint32_t name = thug_crc32_string(p->name_context->name);
        if (name != 0xef24413b && name != 0x89b7dbe4 && name != 0xa84ef276 && name != 0x2fd8e618 && name != 0xeff59585 && name != 0xc692e824) {
            if (!p->reverse_script_requested) {
                p->reverse_script_requested = 1;
                thug_script_run_sync(0xa496aebd, 0, (ThugReferencedObject *)p->body, 0, diagnostics, memory);
            }
            return;
        }
    }
    float negative[4];
    thug_vector_negated(negative, p->body->orientation+8); thug_vector_copy(p->body->orientation+8, negative);
    thug_vector_negated(negative, p->body->orientation); thug_vector_copy(p->body->orientation, negative);
    thug_vector_negated(negative, p->cached_orientation+8); thug_vector_copy(p->cached_orientation+8, negative);
    thug_vector_negated(negative, p->cached_orientation); thug_vector_copy(p->cached_orientation, negative);
    if (!thug_script_get_global_integer(0xb1c84b5a, 0))
        thug_script_run_sync(0x3a8d6ab2, 0, (ThugReferencedObject *)p->body, 0, diagnostics, memory);
}

/* 0x004ffb10. Record the elapsed hold, clear its state/button latch, then
 * deliver the event. No post-event writes overwrite callback changes. */
uint8_t thug_skater_handle_input_release(ThugSkaterPhysics *p, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugSkaterState *state = p->state;
    ThugInputButton *button = &p->input->button_1c0;
    if (!state->drag_coefficient_selector || button->pressed) return 0;
    uint32_t previous = state->drag_selector_time;
    p->input_release_elapsed = thug_elapsed_time()+(thug_timer_offset-previous);
    state = p->state;
    if (state->drag_coefficient_selector) {
        state->drag_coefficient_selector = 0;
        state->drag_selector_time = thug_elapsed_time()+thug_timer_offset;
    }
    thug_input_button_clear_pending(button);
    thug_object_emit_event((ThugReferencedObject *)p->body, 0x8ffefb28, 0, diagnostics, memory);
    return 1;
}

/* 0x004fe320. Branch selection used by the grounded update at 0x0050ee70. */
uint8_t thug_skater_should_brake(const ThugSkaterPhysics *p) {
    const ThugSkaterInput *input = p->input;
    if (!p->acceleration_requested && !input->button_180.pressed && speed(p->body->velocity) < 50) return 1;
    if (!input->button_40.pressed || !p->brake_input_enabled) return 0;
    if (speed(p->body->velocity) < 50 || (!input->button_80.pressed && !input->button_60.pressed)) return 1;
    const float *v = p->body->velocity, *forward = p->body->orientation + 8;
    double dot = r24(r24((double)v[2] * forward[2]) + r24((double)v[1] * forward[1]));
    return r24(dot + r24((double)forward[0] * v[0])) < 0;
}

/* 0x004fe420. Also used by the slope-turn path (0x00501b00). Both thresholds
 * are strict, and unordered comparisons inhibit this predicate. */
uint8_t thug_skater_braking_inhibited(const ThugSkaterPhysics *p) {
    float magnitude = (float)speed(p->body->velocity);
    if (!(thug_script_get_global_number(0x62a1fa03, 1) > magnitude)) return 0;
    return thug_script_get_global_number(0xc3527ef2, 1) > p->orientation_target[1];
}

/* 0x004fe490. TEST AH,5 / JP accepts both an ordered >= result and unordered. */
uint8_t thug_skater_can_accelerate(const ThugSkaterPhysics *p) {
    if (p->acceleration_blocked || (!p->acceleration_requested && !p->input->button_180.pressed)
            || p->input->button_40.pressed) return 0;
    float magnitude = (float)speed(p->body->velocity);
    uint32_t name = p->state->drag_coefficient_selector || p->alternate_acceleration ? 0x92e0247c : 0x4610c2e3;
    return !(thug_skater_stat_parameter(p->body, name) < magnitude);
}

/* 0x004fe530. The Z/W products and X/W deltas spill to float, whereas other
 * intermediate products stay on the x87 stack. Normalization preserves W. */
void thug_skater_accelerate(ThugSkaterPhysics *p) {
    float direction[4];
    for (unsigned i = 0; i < 4; ++i) direction[i] = p->body->orientation[i + 8];
    if (p->accelerate_along_velocity) {
        const float *v = p->body->velocity;
        double sum = r24(r24((double)v[2] * v[2]) + r24((double)v[1] * v[1]));
        double length = r24(__builtin_sqrt(r24(sum + r24((double)v[0] * v[0]))));
        if (!(length < 0.5)) {
            for (unsigned i = 0; i < 4; ++i) direction[i] = v[i];
            thug_vector_normalize(direction);
        }
    }
    uint32_t name = p->state->drag_coefficient_selector || p->alternate_acceleration ? 0x3d24128e : 0x5f9b864d;
    double rate = thug_skater_stat_parameter(p->body, name);
    float stored_rate = (float)rate, dt = p->time_step;
    double dx = r24(rate * direction[0]);
    double dy = r24((double)direction[1] * stored_rate);
    float dz = (float)r24((double)direction[2] * stored_rate);
    float dw = (float)r24((double)direction[3] * stored_rate);
    float delta_x = (float)r24(dx * dt), delta_w = (float)r24((double)dw * dt);
    dy = r24(dy * dt);
    double delta_z = r24((double)dz * dt);
    float *v = p->body->velocity;
    v[0] = (float)r24((double)delta_x + v[0]);
    v[1] = (float)r24(dy + v[1]);
    v[2] = (float)r24(delta_z + v[2]);
    v[3] = (float)r24((double)delta_w + v[3]);
}

/* 0x005019e0. Stop below twice the per-step decrement; otherwise add a vector
 * of negative length. That helper retains W, so this branch doubles velocity W. */
void thug_skater_brake(ThugSkaterPhysics *p) {
    p->braking = 1;
    if (thug_skater_braking_inhibited(p)) { p->braking = 0; return; }
    const ThugSkaterBody *body = p->body;
    float magnitude = (float)speed(body->velocity);
    double decrement = thug_platform_multiply_x87_single(thug_skater_get_parameter(0xe5d73f6f, 1, body), p->time_step);
    if (r24(decrement + decrement) > magnitude) {
        float *v = p->body->velocity;
        v[0] = v[1] = v[2] = 0; v[3] = 1;
        return;
    }
    float delta[4];
    for (unsigned i = 0; i < 4; ++i) delta[i] = p->body->velocity[i];
    decrement = thug_platform_multiply_x87_single(thug_skater_get_parameter(0xe5d73f6f, 1, body), p->time_step);
    thug_vector_set_length(delta, (float)-decrement);
    for (unsigned i = 0; i < 4; ++i) p->body->velocity[i] += delta[i];
}

/* 0x004ff590. Align a vector with the skater's forward axis, retaining speed
 * and forward/backward sign. Keep the sequential copy's overlap behavior. */
void thug_skater_align_velocity(const ThugSkaterPhysics *p, float v[4]) {
    double magnitude = speed(v);
    if (!(magnitude > (double)0.00001f)) return;
    double inverse = r24(1 / magnitude);
    for (unsigned i = 0; i < 4; ++i) v[i] = (float)r24(inverse * v[i]);
    const float *f = p->body->orientation + 8;
    double dot = r24(r24((double)f[1] * v[1]) + r24((double)f[2] * v[2]));
    dot = r24(dot + r24((double)f[0] * v[0]));
    double factor = dot < 0 ? -magnitude : magnitude;
    v[0] = f[0]; v[1] = f[1]; v[2] = f[2];
    float w = f[3];
    v[0] = (float)r24(factor * v[0]); v[3] = w;
    for (unsigned i = 1; i < 4; ++i) v[i] = (float)r24(factor * v[i]);
}

/* 0x004ff470. State-dependent gravity, including gameplay-flag side effects
 * and an optional falling multiplier. The final product remains in ST(0). */
double thug_skater_gravity(const ThugSkaterPhysics *p) {
    const ThugSkaterBody *body = p->body;
    uint32_t divisor_name = !p->state->ground_transition_flag && !p->state->skip_ground_probe ? 0xc31ca696 : 0x441c38a0;
    float base = (float)thug_skater_get_parameter(0xfaa40754, 1, body);
    float gravity = (float)r24((double)base / thug_script_get_global_number(divisor_name, 1));
    if (thug_gameplay_flag(thug_game_context->gameplay_flags, 0x9c8c6df1)) {
        ThugGameplayFlags *flags = thug_game_context->gameplay_flags;
        uint32_t index = thug_script_get_global_integer(0x9c8c6df1, 0);
        thug_gameplay_flag_set(flags, index);
        gravity = (float)thug_platform_multiply_x87_single(thug_skater_get_parameter(0x0ec128f0, 1, body), gravity);
        thug_last_gameplay_flag = 1;
    }
    float falling = (float)thug_script_get_global_number(0xbe33a41e, 0);
    return falling != 0 && p->body->velocity[1] <= 0 ? r24((double)falling * gravity) : gravity;
}

/* 0x00501b00. Turn toward downhill while the shared low-speed/slope predicate
 * holds. Premultiply the body and cached bases independently, preserving their
 * existing differences. Return true even when the selected angle is zero. */
uint8_t thug_skater_slope_turn(ThugSkaterPhysics *p) {
    if (!thug_skater_braking_inhibited(p)) return 0;
    const float *source = speed(p->body->velocity) < (double)0.001f ? p->body->orientation+8 : p->body->velocity;
    float direction[4];
    for (unsigned i = 0; i < 4; ++i) direction[i] = source[i];
    float downhill[4] = {0,-1,0,1};
    thug_vector_project_plane(downhill,p->orientation_target);
    const ThugSkaterBody *body = p->body;
    double angle = thug_vector_signed_angle(direction,downhill,body->orientation+4);
    float stored_angle = (float)angle;
    double rate = thug_skater_get_parameter(0x7dd5678b,1,body);
    double step = thug_platform_multiply_x87_single(rate,p->time_step);
    if (angle < 0) step = -step;
    float turn = (float)step;
    if (__builtin_fabsf(stored_angle) < __builtin_fabs(step)) turn = stored_angle;
    float rotation[16];
    thug_matrix_rotation_y(rotation,turn);
    thug_matrix_multiply(p->body->orientation,rotation,p->body->orientation);
    thug_matrix_rotation_y(rotation,turn);
    thug_matrix_multiply(p->cached_orientation,rotation,p->cached_orientation);
    return 1;
}

/* 0x00506df0. The shared resistance entry point used by grounded movement.
 * Parameter equality skips the entire chain only when both request flags clear. */
void thug_skater_apply_resistance(ThugSkaterPhysics *p) {
    if (!p->acceleration_requested && !p->state->resistance_requested
            && p->friction == thug_skater_get_parameter(0x78f80ec4,1,p->body)) return;
    thug_skater_apply_drag(p);
    if (!thug_skater_slope_turn(p)) thug_skater_apply_friction(p);
}
