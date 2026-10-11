#ifndef THUG_SCRIPT_EXECUTE_H
#define THUG_SCRIPT_EXECUTE_H
#include "runtime.h"
#include "../platform/diagnostics.h"
typedef struct ThugEvent ThugEvent;
/* Original object/component virtual command slots. The engine supplies actual
 * implementations; these declarations do not implement gameplay commands. */
typedef struct { uint32_t name, component_type; } ThugScriptCommand;
typedef struct {
    uint32_t unknown_0, unknown_4;
    uint32_t (*descriptor)(void *, const ThugScriptCommand *, ThugScriptStructure *, ThugScriptInstance *);
    uint32_t (*checksum)(void *, uint32_t, ThugScriptStructure *, ThugScriptInstance *);
    uint32_t unknown_10;
    void (*receive_event)(void *, ThugEvent *);
    uint32_t unknown_18;
    uint32_t (*active)(void *);
} ThugScriptObjectMethods;
typedef struct {
    uint32_t unknown[11];
    uint32_t (*descriptor)(void *, const ThugScriptCommand *, ThugScriptStructure *, ThugScriptInstance *);
} ThugScriptComponentMethods;
extern char thug_script_unknown_name[20];
extern const char thug_script_missing_format[];
const char *thug_script_debug_name(uint32_t);
const char *thug_script_name_text(uint32_t);
void *thug_script_find_object(uint32_t);
void thug_script_read_parameters(ThugScriptInstance *, const ThugMemory *);
uint32_t thug_script_read_name(ThugScriptInstance *);
uint8_t thug_script_dispatch_descriptor(const ThugScriptCommand *, ThugScriptStructure *, void *owner, ThugScriptInstance *);
uint8_t thug_script_call_descriptor(ThugScriptInstance *, const ThugScriptCommand *, void *owner);
uint8_t thug_script_call_member(ThugScriptInstance *, uint32_t name, void *owner);
/* Internal runtime contract: initialized cache/instances, relocated native and
 * virtual handlers, terminating grammar, successful allocation, <=16 call frames
 * and <=10 loop frames. Diagnostics is required for a missing ordinary command.
 * Heap/scopes and formatted output are explicit platform boundaries. */
void thug_script_run_deferred(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_cleanup(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_setup(ThugScriptInstance *, uint32_t name, const uint8_t *program,
    const ThugScriptStructure *arguments, ThugReferencedObject *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_setup_named(ThugScriptInstance *, uint32_t name,
    const ThugScriptStructure *, ThugReferencedObject *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_push_call(ThugScriptInstance *, uint32_t name, const uint8_t *program,
    const ThugScriptStructure *arguments, ThugReferencedObject *, uint32_t immediate,
    const ThugDiagnostics *, const ThugMemory *);
void thug_script_run_immediate(ThugScriptInstance *, uint32_t name, const ThugScriptStructure *, const ThugDiagnostics *, const ThugMemory *);
uint8_t thug_script_invoke_command(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
void thug_script_conditional(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
uint32_t thug_script_execute(ThugScriptInstance *, const ThugDiagnostics *, const ThugMemory *);
#endif
