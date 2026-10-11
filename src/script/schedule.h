#ifndef THUG_SCRIPT_SCHEDULE_H
#define THUG_SCRIPT_SCHEDULE_H
#include "lifetime.h"
/* These wrappers use the actual executor and message queue. Native/virtual
 * command handlers and the loaded symbol/cache/network state must be supplied
 * by the engine. Synchronous scripts must terminate; waits are not bypassed. */
void thug_script_broadcast_sync(uint32_t name, const ThugScriptStructure *, const ThugReferencedObject *,
    const ThugDiagnostics *, const ThugMemory *);
void thug_script_broadcast_spawn(uint32_t name, const ThugReferencedObject *, uint32_t node_id, uint32_t argument,
    const ThugDiagnostics *, const ThugMemory *);
ThugScriptInstance *thug_script_spawn(uint32_t name, ThugScriptStructure *arguments,
    uint32_t completion_name, const ThugScriptStructure *completion_arguments, uint32_t node_id,
    uint32_t user_value, uint32_t network, uint32_t network_argument, uint32_t persistent,
    uint32_t owner_active_only, const ThugDiagnostics *, const ThugMemory *);
void thug_script_run_sync(uint32_t name, ThugScriptStructure *, ThugReferencedObject *, uint32_t network,
    const ThugDiagnostics *, const ThugMemory *);
void thug_script_update_spawned(const ThugDiagnostics *, const ThugMemory *);
/* The object wrapper requires a script symbol; native spawning returns null. */
ThugScriptInstance *thug_object_spawn_script(ThugReferencedObject *, uint32_t name, uint32_t node_id,
    uint32_t network, uint32_t network_argument, ThugScriptStructure *, const ThugDiagnostics *, const ThugMemory *);
ThugScriptInstance *thug_object_spawn_attached_script(ThugReferencedObject *,uint32_t,ThugScriptStructure *,uint32_t,uint32_t,const ThugDiagnostics *,const ThugMemory *);
#endif
