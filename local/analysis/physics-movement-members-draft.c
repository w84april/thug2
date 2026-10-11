#include "../../src/game/components.h"
#include "../../src/game/rail.h"
#include "../../src/script/delivery.h"

/* 00500e80. Normalize only AL returned by the recovered acceleration predicate. */
uint32_t thug_physics_can_kick_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    (void)params; (void)script;
    return thug_skater_can_accelerate(p) != 0;
}
const uint32_t thug_grind_off_events_draft[3] = {13, 4, 0}; /* 0064bc1c */
/* 00509b70. The real rail-event implementation owns the node/contact/QB path. */
uint32_t thug_physics_trigger_grind_off_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    (void)params; (void)script;
    thug_skater_rail_event(p, thug_grind_off_events_draft, diagnostics, memory);
    return 1;
}
/* Host bridge only; preserve the original three-argument component member ABI. */
uint32_t thug_physics_trigger_grind_off_member_draft(void *p, ThugScriptStructure *params, ThugScriptInstance *script) {
    const ThugEventServices *event = thug_event_services;
    return thug_physics_trigger_grind_off_draft(p, params, script,
        event ? event->diagnostics : thug_component_services->diagnostics,
        event ? event->memory : thug_component_services->memory);
}
