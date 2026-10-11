#include "physics_members.h"
#include "rail.h"
#include "../core/timing.h"
#include "../script/delivery.h"
static uint8_t *state_bytes(void *object) {
    return (uint8_t *)((ThugSkaterPhysics *)object)->state;
}
static void timed(uint8_t *flag, uint8_t value) {
    if (*flag != value) {
        *flag = value;
        uint32_t now = thug_elapsed_time() + thug_timer_offset;
        __builtin_memcpy(flag + 4, &now, 4);
    }
}
/* 004fc840 */
uint32_t thug_physics_cancel_wallpush_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script; timed(state_bytes(p) + 0xb8, 1); return 1;
}
/* 004fcf90. Set the spin gate before checking the timed state flag. */
uint32_t thug_physics_no_spin_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script;
    uint8_t *flag = state_bytes(p) + 0x68;
    ((uint8_t *)p)[0x370] = 1;
    timed(flag, 0); return 1;
}
/* 004fcfc0 */
uint32_t thug_physics_in_bail_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script; timed(state_bytes(p) + 0x70, 1); return 1;
}
/* 004fcff0 */
uint32_t thug_physics_not_in_bail_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script; timed(state_bytes(p) + 0x70, 0); return 1;
}
/* 004fd630. Descriptor name checksum2a547e37 has no confirmed source spelling. */
uint32_t thug_physics_set_vert_air_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script; timed(state_bytes(p) + 0x30, 1); return 1;
}
/* 004fd040. Rail sound is selected only by the exact anonymous checksum.
 * The byte in the sound component is updated even when the timed flag is unchanged. */
uint32_t thug_physics_set_rail_sound_member(void *object, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    ThugSkaterPhysics *p = object;
    uint32_t name = 0;
    thug_script_get_checksum(params, 0, &name, 1);
    uint8_t value = name == 0x8d10119d;
    timed((uint8_t *)p->state + 0x58, value);
    ((uint8_t *)p->sound)[0x1e] = value;
    return 1;
}
const uint32_t thug_state_lip_exit_events[3] = {7, 4, 0}; /* 0064bbd4 */
/* 00509a80. Rail callbacks may change the state pointer/mode; reread after
 * dispatch. Wallride orientation repair happens even for an unknown target. */
uint32_t thug_physics_set_state(ThugSkaterPhysics *p, const ThugScriptStructure *params,
    ThugScriptInstance *script, ThugCollisionQuery *q, const ThugDiagnostics *d, const ThugMemory *m) {
    (void)script;
    uint32_t name = 0;
    thug_script_get_checksum(params, 0, &name, 0);
    if (p->state->mode == 3 && name != 0xa549b57b)
        thug_skater_rail_event(p, thug_state_lip_exit_events, d, m);
    ThugSkaterState *state = p->state;
    if (state->mode != 3 && name == 0xa549b57b) p->rail_node = 0;
    if (state->mode == 2) {
        thug_skater_set_up_vector(p, 0, 1, 0, 1, q);
        thug_matrix_copy(p->cached_orientation, p->body->orientation);
    }
    if (name == 0x439f4704) thug_skater_change_state(p, 1, d, m);
    else if (name == 0x58007c97) {
        ((uint8_t *)p)[0x1c5] = 0; /* Saved collision-result flag, not p+0x2d0. */
        thug_skater_change_state(p, 0, d, m);
    } else if (name == 0xa549b57b) thug_skater_change_state(p, 3, d, m);
    return 1;
}
/* Host bridge only; the original member still has two explicit arguments. */
uint32_t thug_physics_set_state_member(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    const ThugEventServices *event = thug_event_services;
    return thug_physics_set_state(p, params, script, thug_component_services->query,
        event ? event->diagnostics : thug_component_services->diagnostics,
        event ? event->memory : thug_component_services->memory);
}
