#ifndef THUG_SCRIPT_DELIVERY_H
#define THUG_SCRIPT_DELIVERY_H
#include "events.h"
#include "execute.h"
struct ThugEvent {
    uint32_t name, source, target, flags;
    ThugScriptStructure *parameters;
};
typedef struct {
    uint32_t event, target, source, script, kind, phase, depth;
} ThugEventLogEntry;
typedef struct {
    ThugEventLogEntry entries[1024];
    uint32_t next_index;
    uint8_t wrapped;
    char names[256][64];
    ThugObjectLookupTable *name_table;
    uint32_t depth, new_count;
} ThugEventLog;
typedef struct ThugEventReceiver ThugEventReceiver;
typedef struct {
    union { uint32_t unknown_0; void *(*dispose)(ThugEventReceiver *, uint32_t, const ThugMemory *); };
    void (*receive)(ThugEventReceiver *, ThugEvent *);
} ThugEventReceiverMethods;
struct ThugEventReceiver {
    const ThugEventReceiverMethods *methods;
    union { uint32_t unknown_4_to_c[3]; ThugObjectReference owner; };
    ThugEventReceiver *next;
    uint32_t unknown_14, active_calls;
};
typedef struct { uint32_t serial, event, target; } ThugEventWaiter;
/* This is the full event-bearing layout of global 6f0fc0. The existing
 * lookup-only prefix remains usable without an initialized event system. */
typedef struct {
    ThugObjectLookupManager objects;
    ThugEventReceiver *receivers;
    uint32_t unknown_18, dispatch_depth;
    ThugEventLog log;
    uint32_t source_script;
    ThugEventWaiter waiters[40];
} ThugEventManager;
/* Platform services for original fixed-argument event and native QB ABIs.
 * Both dispatchers scope this binding and restore it after nested calls. */
typedef struct { const ThugDiagnostics *diagnostics; const ThugMemory *memory; } ThugEventServices;
extern const ThugEventServices *thug_event_services;
extern const ThugEventReceiverMethods thug_event_receiver_methods;
ThugEventReceiver *thug_event_receiver_initialize(ThugEventReceiver *);
void thug_event_receiver_destroy(ThugEventReceiver *);
void *thug_event_receiver_delete(ThugEventReceiver *, uint32_t, const ThugMemory *);
void thug_event_receiver_set_owner(ThugEventReceiver *, ThugReferencedObject *);
void thug_event_receiver_register(ThugEventManager *, ThugEventReceiver *);
void thug_event_receiver_unregister(ThugEventManager *, ThugEventReceiver *);
void thug_event_record_stopped(ThugEventManager *, const ThugEvent *, uint32_t, uint32_t, const ThugMemory *);
void thug_event_stop_propagation(ThugEvent *, uint32_t, uint32_t, const ThugMemory *);
uint32_t thug_ui_event_controller_index(const ThugEvent *);
extern const char thug_event_log_separator[], thug_event_log_title[], thug_event_log_new_title[];
void thug_event_initialize(ThugEvent *, uint32_t name, uint32_t source, uint32_t target, ThugScriptStructure *);
void thug_event_destroy(ThugEvent *, const ThugMemory *);
void thug_event_log_record(ThugEventLog *, uint32_t event, uint32_t target, uint32_t source,
    uint32_t script, uint32_t kind, uint32_t phase, const ThugMemory *);
void thug_event_log_print(ThugEventLog *, uint32_t new_only, uint32_t unused, const ThugDiagnostics *);
void thug_event_record_handled(ThugEventManager *, const ThugEvent *, uint32_t kind, uint32_t script, const ThugMemory *);
void thug_event_mark_handled(ThugEvent *, uint32_t kind, uint32_t script, const ThugMemory *);
void thug_event_receiver_dispatch(ThugEventReceiver *, ThugEvent *);
void thug_script_events_deliver(ThugScriptEventTable *, ThugEvent *, ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_script_receive_event(ThugScriptInstance *, ThugEvent *, const ThugDiagnostics *, const ThugMemory *);
/* Original internal contracts: initialized manager/lists, valid direct target,
 * valid source object for nonnegative-radius broadcasts, successful allocations,
 * <=256 readable event names of <=63 bytes. Native/virtual callbacks are supplied
 * by the engine. The dispatcher preserves callback mutation and script lifetime. */
uint8_t thug_event_emit(ThugEventManager *, uint32_t event, uint32_t target, uint32_t source,
    ThugScriptStructure *, uint32_t broadcast, float radius, const ThugDiagnostics *, const ThugMemory *);
void thug_object_emit_event(ThugReferencedObject *, uint32_t event, ThugScriptStructure *, const ThugDiagnostics *, const ThugMemory *);
void thug_object_broadcast_event(ThugReferencedObject *, uint32_t event, ThugScriptStructure *, uint32_t unused,
    const ThugDiagnostics *, const ThugMemory *);
#endif
