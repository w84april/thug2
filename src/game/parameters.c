#include "skater.h"
#include <stddef.h>

_Static_assert(offsetof(ThugSkaterBody, parameter_sets_enabled) == 0xbc, "Parameter enable offset");
_Static_assert(offsetof(ThugSkaterBody, components) == 0x100, "Component list offset");
_Static_assert(offsetof(ThugObjectComponent, next) == 0x10, "Component link offset");
_Static_assert(offsetof(ThugSkaterPhysics, parameter_mode_active) == 0x2ed, "Parameter mode flag offset");
_Static_assert(offsetof(ThugSkaterPhysics, parameter_mode) == 0x2f0, "Parameter mode offset");
_Static_assert(offsetof(ThugSkaterPhysics, parameter_mode_fallback) == 0x302, "Parameter fallback flag offset");
_Static_assert(offsetof(ThugSkaterPhysics, drag_override_active) == 0x350, "Drag override flag offset");
_Static_assert(offsetof(ThugSkaterPhysics, drag_override) == 0x35c, "Drag override value offset");
_Static_assert(offsetof(ThugSkaterPhysics, state) == 0x1528, "Skater state pointer offset");

/* 0x0045db90. Return the first component with the requested checksum. */
ThugObjectComponent *thug_object_find_component(const ThugSkaterBody *body, uint32_t type) {
    ThugObjectComponent *component = body->components;
    while (component && component->type != type) component = component->next;
    return component;
}

/* 0x005802e0. The CRCs for "SkaterCorePhysics" and "skater_physics" are
 * 0x5bd63b29 and 0x8cbc89dd. Other mode/set names remain unidentified. */
ThugScriptStructure *thug_skater_parameter_set(const ThugSkaterBody *body) {
    uint32_t set = 0x8cbc89dd;
    if (body && body->parameter_sets_enabled) {
        const ThugSkaterPhysics *physics = (const ThugSkaterPhysics *)thug_object_find_component(body, 0x5bd63b29);
        if (physics->parameter_mode_active) {
            switch (physics->parameter_mode) {
                case 0x3029fb1f: set = 0x8b3b782b; break;
                case 0x61c62b2d: set = 0x05716042; break;
                case 0x86929898: set = 0x8711bc92; break;
                case 0xb2c99bf0: set = 0x871ffb73; break;
                case 0x906f06e2: set = 0x43da544e; break;
                case 0xd8d2d646: set = 0x08c9ad5e; break;
                case 0x14a3a4cf: set = 0xd3d12913; break;
            }
        } else if (physics->parameter_mode_fallback) set = 0xd3d12913;
    }
    return thug_script_get_global_structure(set, 0);
}

/* 0x00580400. Structure values pass through a float local. A global fallback
 * can return an exact int32 in ST(0), so preserve that with the double result. */
double thug_skater_get_parameter(uint32_t name, uint32_t assert_missing, const ThugSkaterBody *body) {
    const ThugScriptStructure *parameters = thug_skater_parameter_set(body);
    float value;
    if (thug_script_get_float(parameters, name, &value, 0)) return value;
    return thug_script_get_global_number(name, assert_missing);
}
/* 0x00580440. The integer accessor uses the same selected parameter structure. */
uint32_t thug_skater_get_integer_parameter(uint32_t name,uint32_t assert_missing,const ThugSkaterBody *body) {
    uint32_t value;
    if (thug_script_get_integer(thug_skater_parameter_set(body),name,&value,0)) return value;
    return thug_script_get_global_integer(name,assert_missing);
}

/* 0x004fe6a0. Fetch both script values even when an override will replace them.
 * Any nonzero override flag, including NaN, activates the replacement. */
void thug_skater_apply_drag(ThugSkaterPhysics *physics) {
    float first = (float)thug_skater_get_parameter(0xbed96eda, 1, physics->body);
    float second = (float)thug_skater_get_parameter(0x1a78b6fc, 1, physics->body);
    if (physics->drag_override_active != 0) first = second = physics->drag_override;
    thug_skater_apply_quadratic_drag(physics,
        physics->state->drag_coefficient_selector ? first : second);
}
