#include "../../src/game/components.h"
#include "../../src/script/values.h"
#include "../../src/script/delivery.h"
#include "../../src/core/timing.h"
#include "../../src/core/number.h"
#include "../../src/platform/math.h"

static uint32_t word_at(const void *p, uint32_t offset) {
    uint32_t value; __builtin_memcpy(&value, (const uint8_t *)p + offset, 4); return value;
}
static const ThugMemory *member_memory(void) {
    return thug_event_services ? thug_event_services->memory : thug_component_services->memory;
}
/* 004fbea0. Seconds take precedence over frames, and a frame means exactly16ms.
 * Float arithmetic retains the original PC24 significand and wider exponent. */
uint32_t thug_physics_airtime_parameter_draft(void *unused, const ThugScriptStructure *params) {
    (void)unused;
    float value = 0;
    thug_script_get_float(params, 0, &value, 0);
    if (thug_script_has_flag(params, 0xd029f619) || thug_script_has_flag(params, 0x49e0ee96))
        return thug_truncate_double_low_word(thug_platform_multiply_x87_single(value, 1000));
    if (thug_script_has_flag(params, 0x019176c5) || thug_script_has_flag(params, 0x4a07c332))
        return thug_truncate_double_low_word(thug_platform_multiply_x87_single(value, 16));
    return thug_truncate_low_word(value);
}
static uint32_t airtime(const ThugSkaterPhysics *p) {
    uint32_t start = word_at(p, 0x380);
    return (p->state->mode == 1 || p->state->mode == 2)
        ? thug_elapsed_time() + thug_timer_offset - start : word_at(p, 0x384) - start;
}
/* 004fc880 and004fc8e0. Elapsed time and thresholds compare unsigned. */
uint32_t thug_physics_airtime_less_than_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script; uint32_t duration = airtime(p);
    return duration < thug_physics_airtime_parameter_draft(p, params);
}
uint32_t thug_physics_airtime_greater_than_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)script; uint32_t duration = airtime(p);
    return duration > thug_physics_airtime_parameter_draft(p, params);
}
/* 004fc940. FILD loads the signed word exactly; the high-half correction rounds
 * before multiplying. The final setter receives the stored float's raw bits. */
uint32_t thug_physics_get_airtime_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script, const ThugMemory *memory) {
    (void)params;
    uint32_t duration = airtime(p);
    double value = (int32_t)duration;
    if ((int32_t)duration < 0) value = thug_platform_round_x87_single(value + 0x1p32);
    float seconds = (float)thug_platform_multiply_x87_single(value, (double)0.001f);
    uint32_t bits; __builtin_memcpy(&bits, &seconds, 4);
    thug_script_set_float_bits(script->arguments, 0xad6bcdb4, bits, memory);
    return 1;
}
/* 004fd580. Each insertion may run allocation callbacks; reload the body and
 * script output structure separately for every coordinate, in original order. */
uint32_t thug_physics_get_matrix_normal_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script, const ThugMemory *memory) {
    (void)params;
    const uint32_t names[3] = {0x7323e97c, 0x0424d9ea, 0x9d2d8850};
    for (uint32_t i = 0; i < 3; ++i) {
        const void *body = (const void *)(uintptr_t)word_at(p, 0xc);
        uint32_t bits = word_at(body, 0x7c + i * 4);
        thug_script_set_float_bits(script->arguments, names[i], bits, memory);
    }
    return 1;
}
/* 004fd5e0. All three source words are captured before the vector allocation. */
uint32_t thug_physics_get_last_ground_pos_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script, const ThugMemory *memory) {
    (void)params;
    uint32_t z = word_at(p, 0x340), y = word_at(p, 0x33c), x = word_at(p, 0x338);
    thug_script_set_vector_bits(script->arguments, 0x7f261953, x, y, z, memory);
    return 1;
}
#define OUTPUT(name,offset,key,setter) \
uint32_t thug_physics_##name##_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script, const ThugMemory *memory) { \
    (void)params; uint32_t bits=word_at(p,offset); setter(script->arguments,key,bits,memory); return 1; }
/* 004fd610 */ OUTPUT(get_last_ground_heading,0x348,0x9bc7fc76,thug_script_set_float_bits)
/* 004fdc30 */ OUTPUT(get_ammo,0x2f8,0x107081d5,thug_script_set_integer)
/* 004fdc50 */ OUTPUT(get_ammo_type,0x2fc,0x1d1a8b59,thug_script_set_checksum)
/* 004fdc70 */ OUTPUT(get_pitch_bail_dir,0x2d4,0xd65efde5,thug_script_set_checksum)
#undef OUTPUT

/* Fixed member ABI adapters are host bridges, not additional recoveries. */
#define MEMBER(name) \
uint32_t thug_physics_##name##_member_draft(void *p,ThugScriptStructure *params,ThugScriptInstance *script) { \
    return thug_physics_##name##_draft(p,params,script,member_memory()); }
MEMBER(get_airtime)
MEMBER(get_matrix_normal)
MEMBER(get_last_ground_pos)
MEMBER(get_last_ground_heading)
MEMBER(get_ammo)
MEMBER(get_ammo_type)
MEMBER(get_pitch_bail_dir)
#undef MEMBER
