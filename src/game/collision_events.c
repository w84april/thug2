#include "collision_events.h"
#include "nodes.h"
#include "stats.h"
#include <stddef.h>
_Static_assert(offsetof(ThugCollisionEventComponent, event_mask) == 0x28, "Event component mask");
_Static_assert(offsetof(ThugCollisionNodeMethods, nodes) == 0x34, "Node-provider method");
/* 0x00434a60. Local nodes take precedence; moving-owner parameters come from
 * the global node table. The three shifted bits are added, including duplicates. */
uint8_t thug_collision_event_start(ThugCollisionEventComponent *component, const uint32_t events[3], uint32_t node_name,
    const ThugScriptArray *local_nodes, const ThugReferencedObject *moving_owner, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptStructure *node = NULL;
    if (!local_nodes) node = thug_node_find(node_name, 0);
    else {
        uint32_t count = local_nodes->count;
        while (count) {
            node = thug_script_array_structure(local_nodes, (int32_t)--count);
            if (thug_node_name(node) == node_name) break;
        }
    }
    ThugScriptStructure *arguments = NULL;
    if (moving_owner) {
        ThugScriptStructure *owner_node = thug_node_find(moving_owner->id, 0);
        if (owner_node) thug_script_get_structure(owner_node, 0x5180a4db, &arguments, 0);
    }
    uint32_t script_name = 0;
    thug_script_get_checksum(node, 0x2ca8a299, &script_name, 0);
    if (!script_name || thug_script_multiplayer_gate(node)) return 0;
    component->event_mask = 0;
    if (events[0]) component->event_mask = UINT32_C(1) << (events[0] & 31);
    if (events[1]) component->event_mask += UINT32_C(1) << (events[1] & 31);
    if (events[2]) component->event_mask += UINT32_C(1) << (events[2] & 31);
    ThugReferencedObject *owner = component->base.owner;
    uint32_t network_argument = thug_script_has_flag(node, 0x23627fd7);
    uint32_t network = thug_script_has_flag(node, 0x20209c31);
    thug_object_spawn_script(owner, script_name, node_name, network, network_argument, arguments, diagnostics, memory);
    return 1;
}
/* 0x00434bf0. The callback owner takes precedence over the persistent moving
 * reference. Reread owner/checksum after the node-provider virtual call. */
uint8_t thug_collision_event_from_probe(ThugCollisionEventComponent *component, const uint32_t events[3], ThugCollisionProbe *probe,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (!probe->result.flag_40 || !probe->result.checksum) return 0;
    if (thug_collision_probe_event_object(probe)) {
        ThugObjectComponent *provider = thug_object_find_component((ThugSkaterBody *)thug_collision_probe_event_object(probe), 0xc472ecc5);
        ThugScriptArray *nodes = provider ? (*(const ThugCollisionNodeMethods **)provider)->nodes(provider) : NULL;
        uint32_t name = probe->result.checksum;
        return thug_collision_event_start(component, events, name, nodes, thug_collision_probe_event_object(probe), diagnostics, memory);
    }
    if (!thug_collision_probe_has_moving_object(probe))
        return thug_collision_event_start(component, events, probe->result.checksum, NULL, NULL, diagnostics, memory);
    if (!thug_collision_probe_moving_object(probe)) return 0;
    ThugObjectComponent *provider = thug_object_find_component((ThugSkaterBody *)thug_collision_probe_moving_object(probe), 0xc472ecc5);
    ThugScriptArray *nodes = provider ? (*(const ThugCollisionNodeMethods **)provider)->nodes(provider) : NULL;
    uint32_t name = probe->result.checksum;
    return thug_collision_event_start(component, events, name, nodes, thug_collision_probe_moving_object(probe), diagnostics, memory);
}
