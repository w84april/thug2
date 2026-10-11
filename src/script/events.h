#ifndef THUG_SCRIPT_EVENTS_H
#define THUG_SCRIPT_EVENTS_H
#include "runtime.h"
#include "../game/stats.h"
typedef struct ThugScriptListener ThugScriptListener;
typedef struct {
    ThugScriptListener *(*dispose)(ThugScriptListener *, uint32_t flags, const ThugMemory *);
} ThugScriptListenerMethods;
struct ThugScriptListener {
    const ThugScriptListenerMethods *methods;
    uint32_t value, unknown_8;
    ThugScriptListener *next, *previous;
};
typedef struct {
    uint32_t event, script, group;
    ThugScriptStructure *parameters;
    uint32_t flags;
} ThugScriptEventEntry;
struct ThugScriptEventTable {
    ThugScriptEventEntry *entries;
    uint32_t count;
    uint8_t alive, stop_iteration, padding[2];
    uint32_t active_calls;
};
/* Original allocator selection 6f0fc8/6f0fd0 and method tables 6478d8/6478dc.
 * Tables contain relocated, recovered deleting destructors. */
extern uint32_t thug_script_listener_pool_index;
extern ThugFixedPool *thug_script_listener_pools[2];
extern const ThugScriptListenerMethods thug_script_listener_methods, thug_script_listener_list_methods;
void thug_script_listener_free(void *, const ThugMemory *);
void thug_script_listener_destroy(ThugScriptListener *);
ThugScriptListener *thug_script_listener_delete(ThugScriptListener *, uint32_t flags, const ThugMemory *);
ThugScriptListener *thug_script_listener_list_delete(ThugScriptListener *, uint32_t flags, const ThugMemory *);
void thug_script_listener_remove(ThugScriptListener *, uint32_t value, const ThugMemory *);
void thug_script_unsubscribe(ThugObjectLookupManager *, uint32_t event, ThugScriptInstance *, const ThugMemory *);
void thug_script_unsubscribe_all(ThugObjectLookupManager *, ThugScriptInstance *, const ThugMemory *);
void thug_script_events_unsubscribe(ThugScriptEventTable *, ThugScriptInstance *, const ThugMemory *);
void thug_script_events_clear_group(ThugScriptEventTable *, uint32_t group, const ThugMemory *);
void thug_script_clear_events(ThugScriptInstance *, const ThugMemory *);
void thug_script_events_destroy(ThugScriptEventTable *, const ThugMemory *);
void thug_script_events_remove(ThugScriptEventTable *, uint32_t event, const ThugMemory *);
void thug_script_remove_event(ThugScriptInstance *, uint32_t event, const ThugMemory *);
void thug_object_remove_event(ThugReferencedObject *, uint32_t event, const ThugMemory *);
#endif
