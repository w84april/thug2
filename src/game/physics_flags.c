#include "stats.h"
#include "physics_members.h"

/* Fixed component member ABI: this, parameters, script. These entries ignore
 * the last two arguments. Offsets are original object layout, not new flags. */
static uint32_t word(const void *object, uint32_t offset) {
    uint32_t value;
    __builtin_memcpy(&value, (const uint8_t *)object + offset, 4);
    return value;
}
static const uint8_t *state(const void *object) {
    return (const uint8_t *)(uintptr_t)word(object, 0x1528);
}
#define MEMBER(name) uint32_t thug_physics_##name##_member(void *object, ThugScriptStructure *parameters, ThugScriptInstance *script)
#define UNUSED() (void)parameters; (void)script
#define SET(name, offset, value) MEMBER(name) { UNUSED(); ((uint8_t *)object)[offset] = value; return 1; }
#define GET(name, offset) MEMBER(name) { UNUSED(); return ((const uint8_t *)object)[offset] != 0; }
#define STATE(name, offset) MEMBER(name) { UNUSED(); return state(object)[offset] != 0; }

/* 004fc780 */ STATE(flipped, 0x28)
/* 004fc7a0 */ MEMBER(switched) {
    UNUSED();
    const uint8_t *owner = (const uint8_t *)(uintptr_t)word(object, 0xc);
    return owner[0x110] ? state(object)[0x28] != 0 : state(object)[0x28] == 0;
}
/* 004fc7e0 */ STATE(crouched, 0x20)
/* 004fc800 */ STATE(first_time_on_rail, 0xc8)
/* 004fc820 */ STATE(skitching, 0x88)
/* 004fc9b0 */ GET(braking, 0x324)
/* 004fbf40 */ SET(can_brake_off, 0x311, 0)
/* 004fbf50 */ SET(can_brake_on, 0x311, 1)
/* 004fbf60 */ SET(can_kick_on, 0x310, 0)
/* 004fbf70 */ SET(can_kick_off, 0x310, 1)
/* 004fbf80 */ SET(force_auto_kick_on, 0x2d9, 1)
/* 004fbf90 */ SET(force_auto_kick_off, 0x2d9, 0)
/* 004fbfa0 */ MEMBER(auto_kick_is_off) { UNUSED(); return ((const uint8_t *)object)[0x2d9] == 0; }
/* 004fc9c0 */ MEMBER(restore_auto_kick) {
    UNUSED();
    const void *owner = (const void *)(uintptr_t)word(object, 0xc);
    uint32_t offset = word(owner, 0x2bc) * 8u + 0x395u;
    ((uint8_t *)object)[0x2d9] = ((const uint8_t *)thug_game_context)[offset];
    return 1;
}
/* 004fbfb0 */ SET(skater_vehicle_on, 0x2ed, 1)
/* 004fbfc0 */ SET(skater_vehicle_off, 0x2ed, 0)
/* 004fbfd0 */ GET(is_skater_on_vehicle, 0x2ed)
/* 004fc000 */ SET(can_spin, 0x370, 0)
/* 004fd020 */ STATE(is_in_bail, 0x70)
/* 004fc010 */ SET(bail_on, 0x371, 1)
/* 004fc020 */ SET(bail_off, 0x371, 0)
/* 004fc030 */ GET(bail_is_on, 0x371)
/* 004fc080 */ GET(bad_ledge, 0x249)
/* 004fc090 */ GET(landed_from_spine, 0x372)
/* 004fc0a0 */ GET(landed_from_vert, 0x373)
/* 004fc0b0 */ SET(set_landed_from_vert, 0x373, 1)
/* 004fc0c0 */ SET(reset_landed_from_vert, 0x373, 0)
/* 004fd1c0 */ STATE(in_vert_air, 0x30)
/* 004fc0d0 */ SET(allow_lip_no_grind, 0x375, 1)
/* 004fc0e0 */ SET(clear_allow_lip_no_grind, 0x375, 0)
/* 004fc0f0 */ SET(no_rail_tricks, 0x3a4, 1)
/* 004fc100 */ SET(allow_rail_tricks, 0x3a4, 0)
/* 004fc1a0 */ SET(in_revert, 0x300, 1)
/* 004fc1b0 */ SET(out_revert, 0x300, 0)
/* 004fc1c0 */ GET(is_in_revert, 0x300)
/* 004fc1d0 */ SET(projectiles_on, 0x2f4, 1)
/* 004fc1e0 */ SET(projectiles_off, 0x2f4, 0)
/* 004fc1f0 */ SET(focus_on, 0x301, 1)
/* 004fc200 */ GET(is_skater_focused, 0x301)
/* 004fc210 */ MEMBER(reset_projectile_input) {
    UNUSED();
    uint32_t value = UINT32_MAX;
    __builtin_memcpy((uint8_t *)object + 0x308, &value, 4);
    return 1;
}
/* 004fc230 */ SET(enter_powerslide, 0x2d8, 1)
/* 004fc240 */ SET(exit_powerslide, 0x2d8, 0)
/* 004fc250 */ SET(moto_skateboard_on, 0x302, 1)
/* 004fc260 */ SET(moto_skateboard_off, 0x302, 0)
/* 004fc270 */ GET(is_on_moto_skateboard, 0x302)
/* 004fc280 */ GET(skater_is_flipping, 0x2db)
/* 004fc290 */ SET(reset_is_flipping, 0x2db, 0)
/* 004fc2a0 */ SET(set_throwing_projectile, 0x14c8, 1)
/* 004fc2b0 */ SET(unset_throwing_projectile, 0x14c8, 0)
/* 004fc2c0 */ GET(is_throwing_projectile, 0x14c8)
/* 004fc2d0 */ SET(end_manual_turnaround, 0x304, 0)
/* 004fc2e0 */ SET(enter_tantrum, 0x1508, 1)
/* 004fc2f0 */ SET(exit_tantrum, 0x1508, 0)
/* 004fc300 */ GET(in_tantrum, 0x1508)
/* 004fc340 */ MEMBER(doing_flip) {
    UNUSED();
    if (!((const uint8_t *)object)[0x2db]) return 0;
    float amount;
    __builtin_memcpy(&amount, (const uint8_t *)object + 0x2e0, 4);
    return amount > 10.0f;
}
/* 004fc310 */ SET(enter_tagging, 0x1509, 1)
/* 004fc320 */ SET(exit_tagging, 0x1509, 0)
/* 004fc330 */ GET(is_tagging, 0x1509)

#undef MEMBER
#undef UNUSED
#undef SET
#undef GET
#undef STATE
