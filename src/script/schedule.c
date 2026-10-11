#include "schedule.h"
#include "parser.h"
#include "serialize.h"
#include "tokens.h"
#include "values.h"
#include "../game/stats.h"
#include "../network/queue.h"
#include <stddef.h>
_Static_assert(offsetof(ThugScriptObjectMethods, active) == 0x1c, "Object activity method");

/* 0x00473350. A failed serialization still queues the two header words. */
void thug_script_broadcast_sync(uint32_t name, const ThugScriptStructure *arguments, const ThugReferencedObject *owner,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugNetworkState *network = thug_network_state;
    if (!thug_network_is_active(network)) return;
    ThugMessageSpec spec; thug_message_spec_initialize(&spec);
    uint8_t payload[1032];
    thug_script_write_word(payload, name); thug_script_write_word(payload + 4, owner ? owner->id : UINT32_MAX);
    uint32_t size = thug_script_serialize_structure(arguments, payload + 8, 1024, 1, NULL);
    ThugQueueClient *client = thug_network_get_client(network, 0);
    spec.data = payload; spec.length = (uint16_t)(size + 8); spec.id = 0x48; spec.delivery = 2; spec.group = 8;
    thug_queue_send_first(client, &spec, diagnostics, memory);
}
/* 0x00473420. The PC copies three uninitialized stack-padding bytes at the end
 * of this packet. The port defines those nonsemantic bytes as zero; the first
 * thirteen bytes and all queue behavior retain the original operations. */
void thug_script_broadcast_spawn(uint32_t name, const ThugReferencedObject *owner, uint32_t node_id, uint32_t argument,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugNetworkState *network = thug_network_state;
    if (!thug_network_is_active(network)) return;
    ThugMessageSpec spec; thug_message_spec_initialize(&spec);
    uint8_t payload[16];
    thug_script_write_word(payload, name); thug_script_write_word(payload + 4, owner ? owner->id : UINT32_MAX);
    thug_script_write_word(payload + 8, node_id); payload[12] = (uint8_t)argument;
    payload[13] = payload[14] = payload[15] = 0;
    ThugQueueClient *client = thug_network_get_client(network, 0);
    spec.data = payload; spec.length = 16; spec.id = 0x49; spec.delivery = 2; spec.group = 8;
    thug_queue_send_first(client, &spec, diagnostics, memory);
}
/* 0x00475420. Native symbols run once in a temporary instance and return null.
 * Bytecode instances are only set up; execution belongs to their caller. */
ThugScriptInstance *thug_script_spawn(uint32_t name, ThugScriptStructure *arguments,
    uint32_t completion_name, const ThugScriptStructure *completion_arguments, uint32_t node_id,
    uint32_t user_value, uint32_t network, uint32_t network_argument, uint32_t persistent,
    uint32_t owner_active_only, const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (symbol && symbol->type == 8) {
        memory->temp_scope(memory->context, 1);
        ThugScriptInstance *script = thug_script_allocate(sizeof(*script), memory);
        if (script) thug_script_initialize(script);
        memory->temp_scope(memory->context, 0);
        thug_script_call_native((ThugScriptNativePredicate)(uintptr_t)symbol->value, arguments, script, diagnostics, memory);
        if (script) { thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory); }
        return NULL;
    }
    ThugScriptInstance *script = thug_script_allocate(sizeof(*script), memory);
    if (script) thug_script_initialize(script);
    thug_script_setup(script, name, NULL, arguments, NULL, diagnostics, memory);
    script->unknown_d4 = user_value; script->node_id = node_id;
    script->flags_cc = ((owner_active_only & 1) << 3) | ((persistent & 1) << 1) | (script->flags_cc & 0xf1) | 1;
    if (completion_name) {
        script->completion_checksum = completion_name;
        ThugScriptStructure *completion = thug_script_structure_allocate(8, memory);
        if (completion) thug_script_structure_initialize(completion);
        script->completion_arguments = completion;
        if (completion_arguments) thug_script_structure_merge(completion, completion_arguments, memory);
    }
    if ((uint8_t)network && thug_network_is_active(thug_network_state))
        thug_script_broadcast_spawn(name, NULL, node_id, network_argument, diagnostics, memory);
    return script;
}
/* 0x00475790. Native/member dispatch passes a null script. Bytecode execution
 * repeats until result zero, including any waits that can progress in the loop. */
void thug_script_run_sync(uint32_t name, ThugScriptStructure *arguments, ThugReferencedObject *owner, uint32_t network,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    ThugScriptSymbol *symbol = thug_script_resolve_symbol(name);
    if (!symbol || (symbol->type != 7 && symbol->type != 8 && symbol->type != 9)) return;
    if ((uint8_t)network) thug_script_broadcast_sync(name, arguments, owner, diagnostics, memory);
    if (symbol->type == 7) {
        memory->temp_scope(memory->context, 1);
        ThugScriptInstance *script = thug_script_allocate(sizeof(*script), memory);
        if (script) thug_script_initialize(script);
        thug_script_setup(script, name, NULL, arguments, owner, diagnostics, memory);
        memory->temp_scope(memory->context, 0);
        while (thug_script_execute(script, diagnostics, memory)) { }
        if (script) { thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory); }
    } else if (symbol->type == 8) {
        thug_script_call_native((ThugScriptNativePredicate)(uintptr_t)symbol->value, arguments, NULL, diagnostics, memory);
    } else if (symbol->type == 9) {
        if (symbol->value) thug_script_dispatch_descriptor((const ThugScriptCommand *)(uintptr_t)symbol->value, arguments, owner, NULL);
        else (*(const ThugScriptObjectMethods **)owner)->checksum(owner, name, arguments, NULL);
    }
}
/* 0x00475920. Capture the next spawned instance before callbacks. New list
 * entries do not automatically run this frame; mass stopping is deferred until
 * the updating byte has been cleared. A paused but finished script can retire. */
void thug_script_update_spawned(const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    thug_script_updating = 1; thug_script_wait_gate = 0;
    for (ThugScriptInstance *script = thug_script_list, *next; script; script = next) {
        next = script->next;
        while (next && !(next->flags_cc & 1)) next = next->next;
        uint8_t flags = script->flags_cc;
        ThugReferencedObject *owner = script->owner.object;
        if ((flags & 1) && (!(flags & 4) || !script->instruction) &&
            (!(flags & 8) || !owner || (uint8_t)(*(const ThugScriptObjectMethods **)owner)->active(owner)) &&
            !thug_script_execute(script, diagnostics, memory)) {
            if (script->completion_checksum)
                thug_script_run_sync(script->completion_checksum, script->completion_arguments, script->owner.object, 0, diagnostics, memory);
            thug_script_destroy(script, diagnostics, memory); thug_script_free(script, memory);
        }
    }
    thug_script_updating = 0;
    if (thug_script_stop_pending) { thug_script_stop_spawned(diagnostics, memory); thug_script_stop_pending = 0; }
}
/* 0x00461480. Broadcast precedes spawning; bind the owner and execute once. */
ThugScriptInstance *thug_object_spawn_script(ThugReferencedObject *owner, uint32_t name, uint32_t node_id,
    uint32_t network, uint32_t network_argument, ThugScriptStructure *arguments,
    const ThugDiagnostics *diagnostics, const ThugMemory *memory) {
    if ((uint8_t)network) thug_script_broadcast_spawn(name, NULL, node_id, network_argument, diagnostics, memory);
    ThugScriptInstance *script = thug_script_spawn(name, arguments, 0, NULL, node_id, 0, 0, 0, 0, 0, diagnostics, memory);
    if (script->owner.object) {
        thug_object_reference_unlink(script->owner.object, &script->owner); script->owner.object = NULL;
    }
    script->owner.object = owner;
    if (owner) thug_object_reference_link(owner, &script->owner);
    thug_script_execute(script, diagnostics, memory);
    return script;
}
