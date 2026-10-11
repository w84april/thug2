#include "lifetime.h"
#include "branches.h"
#include "events.h"
#include "values.h"
#include <stddef.h>

uint32_t thug_script_pool_index;
ThugFixedPool *thug_script_pools[2];
uint8_t thug_script_updating, thug_script_stop_pending;
_Static_assert(offsetof(ThugScriptInstance, completion_arguments) == 0xdc, "Completion arguments");
_Static_assert(offsetof(ThugScriptInstance, reference_target) == 0xec, "Embedded referenced base");
_Static_assert(sizeof(ThugReferenceTarget) == 8, "Referenced base size");
_Static_assert(sizeof(ThugScriptEventTable) == 16, "Event table lifetime fields");

/* 0x00449970. As with other heap adapters, the host initializes memory services.
 * A selected fixed pool controls allocation even when it is exhausted. */
void *thug_script_allocate(uint32_t size, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_pools[thug_script_pool_index];
    return pool ? thug_pool_allocate(pool) : memory->allocate(memory->context, size, 1);
}
/* 0x004499b0. Membership checks include the alternate pool, then generic free. */
void thug_script_free(void *script, const ThugMemory *memory) {
    ThugFixedPool *pool = thug_script_pools[thug_script_pool_index];
    if (pool && thug_pool_contains(pool, script)) { thug_pool_release(pool, script); return; }
    pool = thug_script_pools[thug_script_pool_index ^ 1];
    if (pool && thug_pool_contains(pool, script)) thug_pool_release(pool, script);
    else memory->release(memory->context, script);
}
/* 0x00474420. Deferred code executes during cleanup before unlinking. An event
 * table being dispatched is marked dead; its active caller owns final disposal. */
void thug_script_destroy(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_cleanup(script, diagnostics, memory);
    thug_script_clear_events(script, memory);
    ThugScriptStructure *completion = script->completion_arguments;
    if (completion) {
        thug_script_structure_destroy(completion, memory);
        thug_script_structure_free(completion, memory);
    }
    if (!script->previous) thug_script_list = script->next;
    if (script->next) script->next->previous = script->previous;
    if (script->previous) script->previous->next = script->next;
    thug_script_branch_detach(script);
    ThugScriptEventTable *events = script->events;
    if (events) {
        if (events->active_calls) events->alive = 0;
        else { thug_script_events_destroy(events, memory); memory->release(memory->context, events); }
    }
    --thug_script_count;
    thug_reference_target_destroy(&script->reference_target);
    if (script->owner.object) {
        thug_object_reference_unlink(script->owner.object, &script->owner);
        script->owner.object = NULL;
    }
}
/* 0x004752f0. Execute once, copy current arguments, then destroy even if it
 * yielded. It neither loops until completion nor returns an execution status. */
void thug_script_run_collect(uint32_t name, const ThugScriptStructure *arguments,
    ThugReferencedObject *owner, ThugScriptStructure *output, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptInstance *script = thug_script_allocate(sizeof(*script), memory);
    if (script) thug_script_initialize(script);
    thug_script_setup(script, name, NULL, arguments, owner, diagnostics, memory);
    thug_script_execute(script, diagnostics, memory);
    if (script->arguments) thug_script_structure_merge(output, script->arguments, memory);
    thug_script_destroy(script, diagnostics, memory);
    thug_script_free(script, memory);
}
/* 0x004753c0. During an update, request deferred stopping. Otherwise keep spawned
 * scripts carrying bit 2, and capture each next pointer before destruction. */
void thug_script_stop_spawned(const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (thug_script_updating) { thug_script_stop_pending = 1; return; }
    for (ThugScriptInstance *script = thug_script_list, *next; script; script = next) {
        next = script->next;
        if ((script->flags_cc & 1) && !(script->flags_cc & 2)) {
            thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory);
        }
    }
}
/* 0x004756c0. Null and nonspawned instances are left alone. */
void thug_script_delete_spawned(ThugScriptInstance *script, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if (script && (script->flags_cc & 1)) {
        thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory);
    }
}
/* 0x00475700. Finished ordinary scripts with an event table stay alive. */
void thug_script_collect_finished(const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    for (ThugScriptInstance *script = thug_script_list, *next; script; script = next) {
        next = script->next;
        if (!script->instruction && !(script->flags_cc & 1) && !script->events) {
            thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory);
        }
    }
}
static uint8_t has_owner(const ThugScriptInstance *script, ThugReferencedObject *owner) {
    if (script->owner.object == owner) return 1;
    const ThugScriptCallFrame *frames = (const ThugScriptCallFrame *)script->call_storage;
    for (uint32_t i = 0; (int32_t)i < (int32_t)script->call_depth; ++i)
        if (frames[i].owner == owner) return 1;
    return 0;
}
/* 0x004742b0. Owner matching includes suspended calls; checksum matching only
 * examines the current script. Read the next link after cleanup callbacks. */
void thug_script_stop_owner(ThugReferencedObject *owner, uint32_t name, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    for (ThugScriptInstance *script = thug_script_list; script; script = script->next)
        if (has_owner(script, owner) && (!name || script->checksum == name)) {
            thug_script_cleanup(script, diagnostics, memory); thug_script_clear_events(script, memory);
        }
}
/* 0x00474350. This sibling also searches suspended call checksums. The matching
 * owner and matching checksum need not belong to the same frame. */
void thug_script_stop_owner_stack(ThugReferencedObject *owner, uint32_t name, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    for (ThugScriptInstance *script = thug_script_list; script; script = script->next) {
        if (!has_owner(script, owner)) continue;
        uint8_t found = !name || script->checksum == name;
        const ThugScriptCallFrame *frames = (const ThugScriptCallFrame *)script->call_storage;
        for (uint32_t i = 0; !found && (int32_t)i < (int32_t)script->call_depth; ++i)
            if (frames[i].checksum == name) found = 1;
        if (found) { thug_script_cleanup(script, diagnostics, memory); thug_script_clear_events(script, memory); }
    }
}
/* 0x004756f0. */
void thug_script_stop_all_for_owner(ThugReferencedObject *owner, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_stop_owner(owner, 0, diagnostics, memory);
}
