#include "../../src/game/components.h"

/* 004fbfe0. A missing checksum preserves the existing vehicle identifier. */
uint32_t thug_physics_set_skater_vehicle_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    thug_script_get_checksum(params, 0, (uint32_t *)((uint8_t *)p + 0x2f0), 1);
    return 1;
}
/* 004fc040. Store the byte returned by the actual flag lookup. */
uint32_t thug_physics_lock_velocity_direction_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    ((uint8_t *)p)[0x388] = thug_script_has_flag(params, 0xf649d637);
    return 1;
}
/* 004fc060. Missing or mistyped values retain the old tweak. */
uint32_t thug_physics_set_grind_tweak_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    thug_script_get_integer(params, 0, (uint32_t *)((uint8_t *)p + 0x3a8), 0);
    return 1;
}
/* 004fc180. The literal checksum is stored, without resolving its symbol. */
uint32_t thug_physics_set_ammo_type_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    thug_script_get_checksum(params, 0, (uint32_t *)((uint8_t *)p + 0x2fc), 0);
    return 1;
}
/* 004fd140. The first recognized direction has priority; neither accepts all.
 * Both the stance and last-spin fields are tested as nonzero bytes. */
uint32_t thug_physics_last_spin_was_member_draft(void *object, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script;
    ThugSkaterPhysics *p = object;
    if (thug_script_has_flag(params, 0x47953f00))
        return (((const uint8_t *)p->state)[0x28] != 0) != (((const uint8_t *)p)[0x3a5] != 0);
    if (thug_script_has_flag(params, 0x996d5512))
        return (((const uint8_t *)p->state)[0x28] != 0) == (((const uint8_t *)p)[0x3a5] != 0);
    return 1;
}
