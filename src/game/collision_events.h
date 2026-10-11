#ifndef THUG_COLLISION_EVENTS_H
#define THUG_COLLISION_EVENTS_H
#include "skater.h"
#include "../script/schedule.h"
typedef struct ThugCollisionEventComponent {
    ThugObjectComponent base;
    uint8_t unknown_14_to_27[0x14];
    uint32_t event_mask;
} ThugCollisionEventComponent;
typedef struct {
    uint32_t unknown[13];
    ThugScriptArray *(*nodes)(ThugObjectComponent *);
} ThugCollisionNodeMethods;
/* Node data must exist. A local array is searched backward; on a miss the
 * original uses its first element, so an empty array is not valid input. */
uint8_t thug_collision_event_start(ThugCollisionEventComponent *, const uint32_t events[3], uint32_t node_name,
    const ThugScriptArray *local_nodes, const ThugReferencedObject *moving_owner, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_collision_event_from_probe(ThugCollisionEventComponent *, const uint32_t events[3], ThugCollisionProbe *,
    const ThugDiagnostics *, const ThugMemory *);
#endif
