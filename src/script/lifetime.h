#ifndef THUG_SCRIPT_LIFETIME_H
#define THUG_SCRIPT_LIFETIME_H
#include "execute.h"
#include "../core/memory_state.h"
/* Original globals 6f3548/6f3550 and scheduler/deferred-stop bytes 6f3544/45. */
extern uint32_t thug_script_pool_index;
extern ThugFixedPool *thug_script_pools[2];
extern uint8_t thug_script_updating, thug_script_stop_pending;
void *thug_script_allocate(uint32_t size, const ThugMemory *);
void thug_script_free(void *, const ThugMemory *);
void thug_script_destroy(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_run_collect(uint32_t name, const ThugScriptStructure *arguments,
    ThugReferencedObject *owner, ThugScriptStructure *output, const ThugDiagnostics *, const ThugMemory *);
void thug_script_stop_spawned(const ThugDiagnostics *, const ThugMemory *);
void thug_script_delete_spawned(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_collect_finished(const ThugDiagnostics *, const ThugMemory *);
void thug_script_stop_owner(ThugReferencedObject *, uint32_t name, const ThugDiagnostics *, const ThugMemory *);
void thug_script_stop_owner_stack(ThugReferencedObject *, uint32_t name, const ThugDiagnostics *, const ThugMemory *);
void thug_script_stop_all_for_owner(ThugReferencedObject *, const ThugDiagnostics *, const ThugMemory *);
#endif
